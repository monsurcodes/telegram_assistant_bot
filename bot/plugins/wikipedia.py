from telethon import events

from bot.core.base_plugin import BasePlugin
from bot.middleware.pm_ban_check import pm_ban_check
from bot.middleware.register_command_help import register_help_text
from bot.services.wiki_service import WikiService
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
    @pm_ban_check
    async def wiki_search_handler(self, event: events.NewMessage.Event):
        query = event.pattern_match.group(1)
        if not query:
            await event.reply("Please provide a search term. Example: `/wiki Python (programming language)`", parse_mode="md")
            return

        placeholder_msg = await event.reply("🔎 Searching Wikipedia...")

        try:
            summary = await WikiService.get_summary(query)
            response = f"**Wikipedia summary for [{query}]:**\n\n{summary}"
            if len(response) > 3500:
                response = response[:3500] + "..."
            await placeholder_msg.edit(response, parse_mode="md")
            logger.info(f"Sent Wikipedia summary for query '{query}' to user {event.sender_id}")

        except WikiService.WikiDisambiguationError as e:
            options_str = "\n".join(f"- {opt}" for opt in e.options[:5])
            msg = (
                f"Your query `{query}` may refer to multiple topics. Did you mean:\n{options_str}\n\n"
                f"Please be more specific."
            )
            await placeholder_msg.edit(msg, parse_mode="md")

        except WikiService.WikiPageError:
            await placeholder_msg.edit(f"Sorry, no Wikipedia page found for `{query}`.", parse_mode="md")

        except Exception as e:
            await placeholder_msg.edit("Oops! Something went wrong while fetching Wikipedia summary.")
            logger.error(f"Error in wikipedia search for '{query}': {e}")
