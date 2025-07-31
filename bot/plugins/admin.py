from telethon import events

from bot.core.base_plugin import BasePlugin
from bot.utils.command_patterns import args_command_pattern, command_pattern
from bot.utils.logger import get_logger

logger = get_logger(__name__)


class AdminPlugin(BasePlugin):
    name = "Admin"

    def register(self):
        # Register handler for /kick command with argument
        self.bot.dispatcher.register_handler(self.on_kick_command, events.NewMessage(pattern=args_command_pattern('kick')))

    async def on_kick_command(self, event: events.NewMessage.Event):
        # Extract the argument (expected to be username)
        username = event.pattern_match.group(1)
        if not username:
            await event.respond("Please provide the username to kick, e.g. /kick @baduser")
            return

        username = username.strip()

        # For testing, just respond with a kick confirmation message
        await event.respond(f"Kicked {username}!")
