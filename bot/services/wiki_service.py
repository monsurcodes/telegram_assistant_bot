import wikipedia

from bot.utils.logger import get_logger

logger = get_logger(__name__)


class WikiService:
    class WikiDisambiguationError(Exception):
        def __init__(self, options):
            super().__init__("Disambiguation")
            self.options = options

    class WikiPageError(Exception):
        pass

    @staticmethod
    async def get_summary(query: str, sentences: int = 5) -> str:
        """
        Fetch a Wikipedia summary for the given query.

        Raises:
            WikiDisambiguationError: for ambiguous queries
            WikiPageError: if page not found
            Exception: for other errors
        """
        try:
            summary = wikipedia.summary(query, sentences=sentences, auto_suggest=True, redirect=True)
            return summary
        except wikipedia.DisambiguationError as e:
            logger.warning(f"Wikipedia disambiguation for query '{query}' with options: {e.options}")
            raise WikiService.WikiDisambiguationError(e.options)
        except wikipedia.PageError:
            logger.warning(f"Wikipedia page not found for query '{query}'")
            raise WikiService.WikiPageError(f"No page found for {query}")
        except Exception as e:
            logger.exception(f"Unexpected error for query '{query}': {e}")
            raise
