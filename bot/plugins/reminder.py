from telethon import events
from bot.core.base_plugin import BasePlugin
from bot.utils.command_patterns import args_command_pattern
from bot.utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

class ReminderPlugin(BasePlugin):
    """
    Lets users set reminders like `/remind 30 Drink water`.
    """

    def register(self):
        self.bot.dispatcher.register_handler(
            self.handle_reminder,
            events.NewMessage(pattern=args_command_pattern("remind"))
        )
        logger.info("ReminderPlugin registered handler for /remind command")

    async def handle_reminder(self, event: events.NewMessage.Event):
        args = event.pattern_match.group(1)
        user = await event.get_sender()
        logger.info(f"Received /remind command from user_id={user.id} username='{user.username}' args={args!r}")

        if not args:
            await event.respond("Usage: /remind <seconds> <message>")
            logger.warning(f"/remind command missing arguments from user_id={user.id}")
            return

        parts = args.split(maxsplit=1)
        if len(parts) != 2 or not parts[0].isdigit():
            await event.respond("Please specify time in seconds and a message, e.g. /remind 30 Drink water")
            logger.warning(f"/remind command invalid arguments from user_id={user.id}: {args!r}")
            return

        delay = int(parts[0])
        message = parts[1]

        await event.respond(f"Okay! I will remind you in {delay} seconds.")
        logger.info(f"Scheduling reminder for user_id={user.id} in {delay} seconds: {message!r}")

        asyncio.create_task(self.delayed_reminder(event, delay, message))

    async def delayed_reminder(self, event, delay, message):
        await asyncio.sleep(delay)
        await event.respond(f"⏰ Reminder: {message}")
        user = await event.get_sender()
        logger.info(f"Sent reminder to user_id={user.id}: {message!r}")
