import unittest
from types import SimpleNamespace

from wiki_bot.responses import invocation_context, search_embed


class ResponseTests(unittest.TestCase):
    def test_context_starts_with_command_and_includes_requester_and_input(self) -> None:
        interaction = SimpleNamespace(user=SimpleNamespace(mention="<@123>"))

        context = invocation_context(
            interaction,
            "wiki search",
            input_label="Query",
            input_value="**Ada**",
        )

        self.assertTrue(context.startswith("**Command used:** `/wiki search`"))
        self.assertIn("**Requested by:** <@123>", context)
        self.assertIn(r"\*\*Ada\*\*", context)

    def test_search_results_fit_discord_embed_limit(self) -> None:
        embed = search_embed(
            "large",
            ("a" * 5000, "b" * 5000),
            "https://example.com/wiki.png",
        )

        self.assertLessEqual(len(embed.description), 4096)

    def test_empty_search_has_clear_error(self) -> None:
        embed = search_embed(
            "unknown",
            (),
            "https://example.com/wiki.png",
        )

        self.assertEqual(embed.title, "Wikipedia search results")
        self.assertIn("no search results", embed.description)


if __name__ == "__main__":
    unittest.main()
