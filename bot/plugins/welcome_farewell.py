import random

from telethon import events
from telethon.utils import get_display_name

from bot.constants import WELCOME_MESSAGES, BYE_BYE_MESSAGES
from bot.core.base_plugin import BasePlugin
from bot.utils.logger import get_logger

logger = get_logger(__name__)


class WelcomeFarewellPlugin(BasePlugin):

    def register(self):
        self.bot.dispatcher.register_handler(self.chat_action_handler, events.ChatAction)
        logger.info("WelcomeFarewellPlugin registered for join/leave messages")

    async def chat_action_handler(self, event: events.ChatAction.Event):
        if not (event.is_group or event.is_channel):
            return

        chat = await event.get_chat()
        group = chat.title or "this group"

        # --- Welcome section ---
        if event.user_joined or event.user_added:
            for user in getattr(event, "users", [event.user]):
                mention = self._format_mention(user)
                message_template = random.choice(WELCOME_MESSAGES)
                message = message_template.format(user=mention, group=group)
                try:
                    await event.reply(message)
                    logger.info(f"Sent welcome message to {mention} in {group}")
                except Exception as e:
                    logger.exception(f"Failed to send welcome message: {e}")

        # --- Farewell section ---
        elif event.user_left or event.user_kicked:
            user = getattr(event, "user", None)
            if user:
                mention = self._format_mention(user)
                message_template = random.choice(BYE_BYE_MESSAGES)
                message = message_template.format(user=mention, group=group)
                try:
                    await event.reply(message)
                    logger.info(f"Sent goodbye message to {mention} in {group}")
                except Exception as e:
                    logger.exception(f"Failed to send bye bye message: {e}")

    def _format_mention(self, user):
        name = get_display_name(user)
        if user.username:
            return f"@{user.username}"
        # fallback mention with tg text mention (needs user id)
        return f'<a href="tg://user?id={user.id}">{name}</a>'
