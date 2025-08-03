import wikipedia
from telethon import events

from bot.core.base_plugin import BasePlugin
from bot.middleware.register_command_help import register_help_text
from bot.utils.command_patterns import args_command_pattern
from bot.utils.logger import get_logger

logger = get_logger(__name__)

class WikiPlugin(BasePlugin):
    name = "Wikipedia"

    def register(self):
        self.bot.dispatcher.register_handler(
            self.wiki_search_handler,
            events.NewMessage(pattern=args_command_pattern("wiki"))
        )
        logger.info("WikiPlugin registered /wiki command")

    @register_help_text(
        "/wiki <query>",
        "Fetch a summary from Wikipedia for the given query. Example: /wiki Python (programming language)"
    )
    async def wiki_search_handler(self, event: events.NewMessage.Event):
        query = event.pattern_match.group(1)
        if not query:
            await event.reply("Please provide a search term. Example: `/wiki Python`", parse_mode="md")
            return

        try:
            # Use wikipedia summary with a limit on sentences
            summary = wikipedia.summary(query, sentences=5, auto_suggest=True, redirect=True)

            # Optionally limit length to avoid very long messages
            # if len(summary) > 1000:
            #     summary = summary[:1000] + "..."

            response = f"**Wikipedia summary for [{query}]:**\n\n{summary}"
            await event.reply(response, parse_mode="md")
            logger.info(f"Sent Wikipedia summary for query '{query}' to user {event.sender_id}")

        except wikipedia.DisambiguationError as e:
            options = e.options[:5]  # Give user up to 5 options to choose from
            options_str = "\n".join(f"- {opt}" for opt in options)
            msg = (
                f"Your query `{query}` may refer to multiple topics. Did you mean:\n{options_str}\n\n"
                f"Please be more specific."
            )
            await event.reply(msg, parse_mode="md")
            logger.warning(f"Wikipedia disambiguation for query '{query}'")

        except wikipedia.PageError:
            await event.reply(f"Sorry, no Wikipedia page found for `{query}`.", parse_mode="md")
            logger.warning(f"Wikipedia page not found for query '{query}'")

        except Exception as e:
            await event.reply("Oops! Something went wrong while fetching Wikipedia summary.")
            logger.error(f"Error in wikipedia search for '{query}': {e}")
