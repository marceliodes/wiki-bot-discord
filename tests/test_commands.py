import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import discord
from discord import app_commands

from wiki_bot.commands import WikiCommandGroup
from wiki_bot.service import Article, ArticleNotFound


class CommandMetadataTests(unittest.TestCase):
    def test_wiki_group_exposes_expected_command_schema(self) -> None:
        service = MagicMock()
        service.default_thumbnail_url = "https://example.com/wiki.png"
        group = WikiCommandGroup(service)
        client = discord.Client(intents=discord.Intents.none())
        tree = app_commands.CommandTree(client)
        tree.add_command(group)

        payload = group.to_dict(tree)
        commands = {option["name"]: option for option in payload["options"]}

        self.assertEqual(
            set(commands), {"search", "article", "random", "about", "help"}
        )
        search_input = commands["search"]["options"][0]
        article_input = commands["article"]["options"][0]
        self.assertEqual(
            (search_input["name"], search_input["required"]), ("query", True)
        )
        self.assertEqual(
            (article_input["name"], article_input["required"]), ("title", True)
        )
        self.assertEqual(
            (search_input["min_length"], search_input["max_length"]), (1, 200)
        )
        self.assertEqual(
            (article_input["min_length"], article_input["max_length"]), (1, 200)
        )


class CommandInteractionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.service = MagicMock()
        self.service.default_thumbnail_url = "https://example.com/wiki.png"
        self.group = WikiCommandGroup(self.service)
        self.interaction = MagicMock()
        self.interaction.user.mention = "<@123>"
        self.interaction.response.defer = AsyncMock()
        self.interaction.response.send_message = AsyncMock()
        self.interaction.response.is_done.return_value = False
        self.interaction.edit_original_response = AsyncMock()
        self.interaction.client.user = SimpleNamespace(name="Wiki Bot")

    async def test_search_defers_publicly_and_edits_contextual_response(self) -> None:
        self.service.search = AsyncMock(return_value=("Ada Lovelace",))
        command = self.group.get_command("search")

        await command.callback(self.group, self.interaction, "Ada")

        self.interaction.response.defer.assert_awaited_once_with(thinking=True)
        kwargs = self.interaction.edit_original_response.await_args.kwargs
        self.assertTrue(kwargs["content"].startswith("**Command used:** `/wiki search`"))
        self.assertIn("**Query:** “Ada”", kwargs["content"])
        self.assertEqual(kwargs["embed"].description, "Ada Lovelace")
        self.assertFalse(kwargs["allowed_mentions"].everyone)
        self.assertFalse(kwargs["allowed_mentions"].users)

    async def test_article_error_keeps_invocation_context(self) -> None:
        self.service.article = AsyncMock(side_effect=ArticleNotFound("Missing"))
        command = self.group.get_command("article")

        await command.callback(self.group, self.interaction, "Missing")

        kwargs = self.interaction.edit_original_response.await_args.kwargs
        self.assertIn("`/wiki article`", kwargs["content"])
        self.assertIn("“Missing”", kwargs["content"])
        self.assertEqual(kwargs["embed"].title, "Article not found")

    async def test_random_returns_contextual_article(self) -> None:
        self.service.random_article = AsyncMock(
            return_value=Article(
                title="Random",
                summary="Summary",
                url="https://en.wikipedia.org/wiki/Random",
                thumbnail_url="https://example.com/random.png",
            )
        )
        command = self.group.get_command("random")

        await command.callback(self.group, self.interaction)

        kwargs = self.interaction.edit_original_response.await_args.kwargs
        self.assertTrue(kwargs["content"].startswith("**Command used:** `/wiki random`"))
        self.assertEqual(kwargs["embed"].title, "Random")

    async def test_unexpected_failure_returns_safe_contextual_error(self) -> None:
        self.service.search = AsyncMock(side_effect=RuntimeError("private detail"))
        command = self.group.get_command("search")

        with self.assertLogs("wiki_bot.commands", level="ERROR"):
            await command.callback(self.group, self.interaction, "Ada")

        kwargs = self.interaction.edit_original_response.await_args.kwargs
        self.assertIn("`/wiki search`", kwargs["content"])
        self.assertEqual(kwargs["embed"].title, "Error")
        self.assertNotIn("private detail", kwargs["embed"].description)

    async def test_help_is_an_immediate_public_contextual_response(self) -> None:
        command = self.group.get_command("help")

        await command.callback(self.group, self.interaction)

        kwargs = self.interaction.response.send_message.await_args.kwargs
        self.assertTrue(kwargs["content"].startswith("**Command used:** `/wiki help`"))
        self.assertNotIn("ephemeral", kwargs)
        self.assertIn("/wiki article", kwargs["embed"].description)

    async def test_group_error_handler_returns_context_for_uncaught_error(self) -> None:
        self.interaction.command = self.group.get_command("article")
        self.interaction.namespace = SimpleNamespace(title="Missing")

        with self.assertLogs("wiki_bot.commands", level="ERROR"):
            await self.group.on_error(
                self.interaction,
                app_commands.AppCommandError("failed"),
            )

        kwargs = self.interaction.response.send_message.await_args.kwargs
        self.assertIn("`/wiki article`", kwargs["content"])
        self.assertIn("“Missing”", kwargs["content"])
        self.assertEqual(kwargs["embed"].title, "Error")


if __name__ == "__main__":
    unittest.main()
