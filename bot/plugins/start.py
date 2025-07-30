from telethon import events, errors
from bot.core.base_plugin import BasePlugin
from bot.utils.command_patterns import command_pattern
from bot.constants import START_MESSAGE, OWNER_START_MESSAGE
from bot.middleware.owner_check import owner_only
from bot.config import OWNER_ID
from bot.utils.logger import get_logger
from bot.db.crud.user_crud import UserCRUD
from bot.db.db_session import db

logger = get_logger(__name__)

user_crud = UserCRUD(db)

class StartPlugin(BasePlugin):
    """
    Handles basic commands functionality including:
    - Welcoming new users when they join
    - Responding to /start command with a welcome message
    """

    def register(self):
        # Register handler for /start
        self.bot.dispatcher.register_handler(self.on_start_command, events.NewMessage(pattern=command_pattern('start')))

        # Register handler for /start
        self.bot.dispatcher.register_handler(self.on_help_command, events.NewMessage(pattern=command_pattern('help')))

    async def on_start_command(self, event: events.NewMessage.Event):
        # Respond to /start command with welcome message
        try:
            user = await event.get_sender()
            if int(user.id) == int(OWNER_ID):
                await event.respond(OWNER_START_MESSAGE.format(user.first_name))
            else:
                await user_crud.create_user({
                    '_id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                    'access_hash': user.access_hash,
                    'photo': {
                        'photo_id': user.photo.photo_id,
                        'dc_id': user.photo.dc_id,
                        'has_video': user.photo.has_video
                    } if user.photo else None,
                })

                await event.respond(START_MESSAGE.format(user.first_name))
        except Exception as e:
            logger.exception(e)
            await event.respond("Failed to send start message. Check bot logs for details.")

    @owner_only
    async def on_help_command(self, event: events.NewMessage.Event):
        # Respond to /help command with help message
        await event.respond("You are the owner! Executing super-secret command.")