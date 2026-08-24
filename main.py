"""Application entry point for the Discord Wikipedia bot."""

from __future__ import annotations

import logging
import os

import discord
from discord import app_commands
from dotenv import load_dotenv

from wiki_bot.commands import WikiCommandGroup
from wiki_bot.service import WikipediaService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class WikipediaBot(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.wiki_commands = WikiCommandGroup(WikipediaService(language="en"))

    async def setup_hook(self) -> None:
        self.tree.add_command(self.wiki_commands)
        synced_commands = await self.tree.sync()
        logger.info("Synced %d global application command(s)", len(synced_commands))

    async def on_ready(self) -> None:
        await self.change_presence(activity=discord.Game("/wiki help"))
        logger.info("Bot in %d server(s)", len(self.guilds))
        logger.info("Bot name: %s", self.user.name if self.user else "unknown")


def main() -> None:
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN is missing from the environment or .env file")
        return

    bot = WikipediaBot()
    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Discord rejected DISCORD_TOKEN")


if __name__ == "__main__":
    main()
