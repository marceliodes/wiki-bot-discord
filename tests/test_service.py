import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from wikipedia.exceptions import DisambiguationError, PageError

from wiki_bot.service import (
    ArticleAmbiguous,
    ArticleNotFound,
    RandomArticleUnavailable,
    WikipediaService,
)


class WikipediaServiceTests(unittest.TestCase):
    def test_search_limits_results(self) -> None:
        service = WikipediaService()
        with patch(
            "wiki_bot.service.wikipedia.search",
            return_value=["Ada Lovelace", "Ada"],
        ) as search:
            results = service._search("Ada")

        self.assertEqual(results, ("Ada Lovelace", "Ada"))
        search.assert_called_once_with("Ada", results=20, suggestion=False)

    def test_article_returns_canonical_page_data(self) -> None:
        page = SimpleNamespace(
            title="Ada Lovelace",
            url="https://en.wikipedia.org/wiki/Ada_Lovelace",
            images=["https://example.com/ada.png"],
        )
        service = WikipediaService()

        with patch(
            "wiki_bot.service.wikipedia.page", return_value=page
        ), patch(
            "wiki_bot.service.wikipedia.summary",
            return_value="Ada was an English mathematician.",
        ) as summary:
            article = service._article("ada lovelace")

        self.assertEqual(article.title, "Ada Lovelace")
        self.assertEqual(article.thumbnail_url, "https://example.com/ada.png")
        summary.assert_called_once_with("Ada Lovelace", sentences=5)

    def test_article_uses_default_thumbnail_when_page_has_no_images(self) -> None:
        page = SimpleNamespace(
            title="Test",
            url="https://en.wikipedia.org/wiki/Test",
            images=[],
        )
        service = WikipediaService()

        with patch(
            "wiki_bot.service.wikipedia.page", return_value=page
        ), patch("wiki_bot.service.wikipedia.summary", return_value="Summary"):
            article = service._article("Test")

        self.assertEqual(article.thumbnail_url, service.default_thumbnail_url)

    def test_article_normalizes_not_found_error(self) -> None:
        service = WikipediaService()
        with patch(
            "wiki_bot.service.wikipedia.page", side_effect=PageError("Missing")
        ):
            with self.assertRaises(ArticleNotFound):
                service._article("Missing")

    def test_article_normalizes_disambiguation_error(self) -> None:
        service = WikipediaService()
        error = DisambiguationError("Mercury", ["Mercury planet", "Mercury element"])
        with patch("wiki_bot.service.wikipedia.page", side_effect=error):
            with self.assertRaises(ArticleAmbiguous):
                service._article("Mercury")

    def test_random_article_stops_after_retry_limit(self) -> None:
        service = WikipediaService(random_attempts=5)
        error = DisambiguationError("Random", ["Randomness"])

        with patch(
            "wiki_bot.service.wikipedia.random",
            return_value="Random",
        ) as random_page, patch(
            "wiki_bot.service.wikipedia.page", side_effect=error
        ):
            with self.assertRaises(RandomArticleUnavailable):
                service._random_article()

        self.assertEqual(random_page.call_count, 5)


class ExecutorBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def test_run_submits_work_to_an_executor(self) -> None:
        service = WikipediaService()
        loop = MagicMock()
        loop.run_in_executor = AsyncMock(return_value="result")

        with patch("wiki_bot.service.asyncio.get_running_loop", return_value=loop):
            result = await service._run(str.upper, "wiki")

        self.assertEqual(result, "result")
        executor, operation = loop.run_in_executor.await_args.args
        self.assertIsNone(executor)
        self.assertEqual(operation(), "WIKI")


if __name__ == "__main__":
    unittest.main()
