"""Shared Discord message and embed presentation helpers."""

from __future__ import annotations

from typing import Iterable, Optional

import discord

from .service import Article, ArticleAmbiguous, ArticleNotFound


ERROR_COLOR = 0xE74C3C
DEFAULT_COLOR = 0x000000
MAX_EMBED_DESCRIPTION = 4096


def invocation_context(
    interaction: discord.Interaction,
    command: str,
    *,
    input_label: Optional[str] = None,
    input_value: Optional[str] = None,
) -> str:
    """Build the public line that explains why the bot replied."""

    requester = interaction.user.mention
    context = f"**Command used:** `/{command}` • **Requested by:** {requester}"
    if input_label and input_value is not None:
        safe_value = discord.utils.escape_markdown(input_value)
        context += f" • **{input_label}:** “{safe_value}”"
    return context


def search_embed(
    query: str, results: Iterable[str], thumbnail_url: str
) -> discord.Embed:
    result_list = tuple(results)
    if not result_list:
        embed = discord.Embed(
            title="Wikipedia search results",
            color=ERROR_COLOR,
            description=f"Sorry, there are no search results for '{query}'.",
        )
    else:
        embed = discord.Embed(
            title="Wikipedia search results",
            color=DEFAULT_COLOR,
            description=_fit_lines(result_list),
        )
    embed.set_thumbnail(url=thumbnail_url)
    return embed


def article_embed(article: Article) -> discord.Embed:
    description = f"{article.summary}\n\n[Read further]({article.url})"
    embed = discord.Embed(
        title=article.title,
        color=DEFAULT_COLOR,
        description=_truncate(description, MAX_EMBED_DESCRIPTION),
    )
    embed.set_thumbnail(url=article.thumbnail_url)
    return embed


def article_error_embed(error: Exception, thumbnail_url: str) -> discord.Embed:
    if isinstance(error, ArticleAmbiguous):
        title = "Ambiguous article"
        description = (
            "That title matches multiple Wikipedia articles. Use `/wiki search` "
            "to find a more specific title, then try `/wiki article` again."
        )
    elif isinstance(error, ArticleNotFound):
        title = "Article not found"
        description = (
            "Wikipedia has no article with that title. Use `/wiki search` to "
            "find the correct title."
        )
    else:
        title = "Wikipedia unavailable"
        description = (
            "A valid random article could not be loaded after several attempts. "
            "Please try again."
        )

    embed = discord.Embed(title=title, color=ERROR_COLOR, description=description)
    embed.set_thumbnail(url=thumbnail_url)
    return embed


def unexpected_error_embed(thumbnail_url: str) -> discord.Embed:
    embed = discord.Embed(
        title="Error",
        color=ERROR_COLOR,
        description="Sorry, an unexpected error occurred. Please try again.",
    )
    embed.set_thumbnail(url=thumbnail_url)
    return embed


def about_embed(bot_name: str, thumbnail_url: str) -> discord.Embed:
    description = (
        f"{bot_name} is built using the "
        "[Wikipedia API](https://wikipedia.readthedocs.io/en/latest/code.html). "
        "Wikipedia articles are available under the "
        "[Creative Commons Attribution-ShareAlike License]"
        "(https://en.wikipedia.org/wiki/"
        "Wikipedia:Text_of_Creative_Commons_Attribution-ShareAlike_3.0_Unported_License)."
        "\n\n[Wikipedia Official Site](https://en.wikipedia.org/wiki/Main_Page)"
    )
    embed = discord.Embed(
        title="About",
        color=DEFAULT_COLOR,
        description=description,
    )
    embed.set_thumbnail(url=thumbnail_url)
    return embed


def help_embed(thumbnail_url: str) -> discord.Embed:
    description = "\n".join(
        (
            "`/wiki search query:<text>` — find matching Wikipedia article titles.",
            "`/wiki article title:<text>` — show a five-sentence article summary.",
            "`/wiki random` — show a random Wikipedia article.",
            "`/wiki about` — show information and licensing credits.",
            "`/wiki help` — show this command list.",
        )
    )
    embed = discord.Embed(
        title="Wikipedia bot commands",
        color=DEFAULT_COLOR,
        description=description,
    )
    embed.set_thumbnail(url=thumbnail_url)
    return embed


def _fit_lines(lines: Iterable[str]) -> str:
    selected: list[str] = []
    current_length = 0

    for line in lines:
        separator_length = 1 if selected else 0
        available = MAX_EMBED_DESCRIPTION - current_length - separator_length
        if available <= 1:
            break
        selected.append(_truncate(str(line), available))
        current_length += separator_length + len(selected[-1])
        if current_length >= MAX_EMBED_DESCRIPTION:
            break

    return "\n".join(selected)


def _truncate(value: str, maximum: int) -> str:
    if len(value) <= maximum:
        return value
    if maximum <= 1:
        return value[:maximum]
    return value[: maximum - 1] + "…"
