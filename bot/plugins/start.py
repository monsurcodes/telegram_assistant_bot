from telethon import events

from bot.config import OWNER_ID
from bot.constants import START_MESSAGE, OWNER_START_MESSAGE
from bot.core.base_plugin import BasePlugin
from bot.db.crud.user_crud import UserCRUD
from bot.db.db_session import db
from bot.utils.command_patterns import command_pattern
from bot.utils.logger import get_logger

logger = get_logger(__name__)

user_crud = UserCRUD(db)


class StartPlugin(BasePlugin):

    def register(self):
        # Register handler for /start
        self.bot.dispatcher.register_handler(self.on_start_command, events.NewMessage(pattern=command_pattern('start')))

    async def on_start_command(self, event: events.NewMessage.Event):
        # reply to /start command with welcome message
        try:
            user = await event.get_sender()
            if int(user.id) == int(OWNER_ID):
                await event.reply(OWNER_START_MESSAGE.format(user.first_name))
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

                await event.reply(START_MESSAGE.format(user.first_name))
        except Exception as e:
            logger.exception(e)
            await event.reply("Failed to send start message. Check bot logs for details.")
