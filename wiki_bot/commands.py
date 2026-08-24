"""Discord slash commands for Wikipedia operations."""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

import discord
from discord import app_commands

from .responses import (
    about_embed,
    article_embed,
    article_error_embed,
    help_embed,
    invocation_context,
    search_embed,
    unexpected_error_embed,
)
from .service import WikipediaService, WikipediaServiceError


logger = logging.getLogger(__name__)
NO_MENTIONS = discord.AllowedMentions.none()


class WikiCommandGroup(app_commands.Group):
    """The public ``/wiki`` command group."""

    def __init__(self, service: WikipediaService) -> None:
        super().__init__(
            name="wiki",
            description="Search, read, and explore Wikipedia.",
        )
        self.service = service

    @app_commands.command(name="search", description="Search Wikipedia article titles.")
    @app_commands.describe(query="Text to search for on Wikipedia.")
    async def search(
        self,
        interaction: discord.Interaction,
        query: app_commands.Range[str, 1, 200],
    ) -> None:
        context = invocation_context(
            interaction,
            "wiki search",
            input_label="Query",
            input_value=query,
        )
        await self._run_deferred(
            interaction,
            context,
            lambda: self.service.search(query),
            lambda results: search_embed(
                query, results, self.service.default_thumbnail_url
            ),
        )

    @app_commands.command(
        name="article", description="Show a summary of a Wikipedia article."
    )
    @app_commands.describe(title="Title of the Wikipedia article to show.")
    async def article(
        self,
        interaction: discord.Interaction,
        title: app_commands.Range[str, 1, 200],
    ) -> None:
        context = invocation_context(
            interaction,
            "wiki article",
            input_label="Title",
            input_value=title,
        )
        await self._run_deferred(
            interaction,
            context,
            lambda: self.service.article(title),
            article_embed,
        )

    @app_commands.command(
        name="random", description="Show a random Wikipedia article."
    )
    async def random(self, interaction: discord.Interaction) -> None:
        context = invocation_context(interaction, "wiki random")
        await self._run_deferred(
            interaction,
            context,
            self.service.random_article,
            article_embed,
        )

    @app_commands.command(name="about", description="Show information about the bot.")
    async def about(self, interaction: discord.Interaction) -> None:
        context = invocation_context(interaction, "wiki about")
        bot_name = interaction.client.user.name if interaction.client.user else "This bot"
        await interaction.response.send_message(
            content=context,
            embed=about_embed(bot_name, self.service.default_thumbnail_url),
            allowed_mentions=NO_MENTIONS,
        )

    @app_commands.command(name="help", description="Show all Wikipedia bot commands.")
    async def help(self, interaction: discord.Interaction) -> None:
        context = invocation_context(interaction, "wiki help")
        await interaction.response.send_message(
            content=context,
            embed=help_embed(self.service.default_thumbnail_url),
            allowed_mentions=NO_MENTIONS,
        )

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
        /,
    ) -> None:
        """Return a contextual reply for failures outside command callbacks."""

        command_name = (
            interaction.command.qualified_name if interaction.command else "wiki"
        )
        input_label = None
        input_value = None
        if command_name == "wiki search":
            input_label = "Query"
            input_value = getattr(interaction.namespace, "query", None)
        elif command_name == "wiki article":
            input_label = "Title"
            input_value = getattr(interaction.namespace, "title", None)

        context = invocation_context(
            interaction,
            command_name,
            input_label=input_label,
            input_value=input_value,
        )
        logger.error(
            "Unhandled application command error for /%s",
            command_name,
            exc_info=(type(error), error, error.__traceback__),
        )
        response = {
            "content": context,
            "embed": unexpected_error_embed(self.service.default_thumbnail_url),
            "allowed_mentions": NO_MENTIONS,
        }
        if interaction.response.is_done():
            await interaction.edit_original_response(**response)
        else:
            await interaction.response.send_message(**response)

    async def _run_deferred(
        self,
        interaction: discord.Interaction,
        context: str,
        operation: Callable[[], Awaitable[Any]],
        build_embed: Callable[[Any], discord.Embed],
    ) -> None:
        await interaction.response.defer(thinking=True)

        try:
            result = await operation()
            embed = build_embed(result)
        except WikipediaServiceError as error:
            embed = article_error_embed(error, self.service.default_thumbnail_url)
        except Exception:
            logger.exception("Unexpected error while handling %s", context)
            embed = unexpected_error_embed(self.service.default_thumbnail_url)

        await interaction.edit_original_response(
            content=context,
            embed=embed,
            allowed_mentions=NO_MENTIONS,
        )
