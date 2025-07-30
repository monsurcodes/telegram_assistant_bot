from telethon import events, errors
from bot.core.base_plugin import BasePlugin
from bot.utils.command_patterns import command_pattern

class StartPlugin(BasePlugin):
    """
    Handles basic commands functionality including:
    - Welcoming new users when they join
    - Responding to /start command with a welcome message
    """

    def register(self):
        # Register handler for new messages (commands)
        self.bot.dispatcher.register_handler(self.on_start_command, events.NewMessage(pattern=command_pattern('start')))

    async def on_start_command(self, event: events.NewMessage.Event):
        # Respond to /start command with welcome message
        user = await event.get_sender()
        await event.respond(
            f"Hello {user.first_name}!\n"
            "Welcome to the bot. Use /help to see what I can do."
        )
