"""Async boundary around the synchronous ``wikipedia`` package."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from functools import partial
from random import choice
from typing import Callable, Optional, Tuple, TypeVar

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError


T = TypeVar("T")


class WikipediaServiceError(Exception):
    """Base class for errors that can be presented safely to Discord users."""


class ArticleNotFound(WikipediaServiceError):
    """Raised when Wikipedia has no page for the supplied title."""


class ArticleAmbiguous(WikipediaServiceError):
    """Raised when a title refers to more than one Wikipedia page."""


class RandomArticleUnavailable(WikipediaServiceError):
    """Raised after the configured random-page retry limit is exhausted."""


@dataclass(frozen=True)
class Article:
    title: str
    summary: str
    url: str
    thumbnail_url: str


class WikipediaService:
    """Fetch Wikipedia data without blocking Discord's asyncio event loop."""

    def __init__(self, language: str = "en", random_attempts: int = 5) -> None:
        if random_attempts < 1:
            raise ValueError("random_attempts must be at least 1")

        self.language = language
        self.random_attempts = random_attempts
        wikipedia.set_lang(language)

    @property
    def default_thumbnail_url(self) -> str:
        return (
            "https://www.wikipedia.org/static/images/project-logos/"
            f"{self.language}wiki.png"
        )

    async def search(self, query: str) -> Tuple[str, ...]:
        return await self._run(self._search, query)

    async def article(self, title: str) -> Article:
        return await self._run(self._article, title)

    async def random_article(self) -> Article:
        return await self._run(self._random_article)

    async def _run(self, function: Callable[..., T], *args: object) -> T:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(function, *args))

    def _search(self, query: str) -> Tuple[str, ...]:
        results = wikipedia.search(query, results=20, suggestion=False)
        return tuple(str(result) for result in results)

    def _article(self, title: str) -> Article:
        try:
            return self._load_article(title)
        except DisambiguationError as error:
            raise ArticleAmbiguous(title) from error
        except PageError as error:
            raise ArticleNotFound(title) from error

    def _random_article(self) -> Article:
        for _ in range(self.random_attempts):
            try:
                title = str(wikipedia.random(pages=1))
                return self._load_article(title)
            except (DisambiguationError, PageError):
                continue

        raise RandomArticleUnavailable

    def _load_article(self, title: str) -> Article:
        page = wikipedia.page(title)
        canonical_title = str(page.title)
        summary = wikipedia.summary(canonical_title, sentences=5)
        thumbnail_url = self._select_thumbnail(getattr(page, "images", None))

        return Article(
            title=canonical_title,
            summary=str(summary),
            url=str(page.url),
            thumbnail_url=thumbnail_url,
        )

    def _select_thumbnail(self, images: Optional[list[str]]) -> str:
        if not images:
            return self.default_thumbnail_url

        try:
            return str(choice(images))
        except Exception:
            return self.default_thumbnail_url
