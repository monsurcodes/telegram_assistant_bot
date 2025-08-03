from telethon import events, Button

from bot.config import OWNER_ID
from bot.constants import START_MESSAGE, OWNER_START_MESSAGE
from bot.core.base_plugin import BasePlugin
from bot.db.crud.user_crud import UserCRUD
from bot.db.db_session import db
from bot.middleware.pm_ban_check import pm_ban_check
from bot.utils.command_patterns import command_pattern
from bot.utils.logger import get_logger

logger = get_logger(__name__)

user_crud = UserCRUD(db)


class StartPlugin(BasePlugin):

    def register(self):
        self.bot.dispatcher.register_handler(
            self.on_start_command,
            events.NewMessage(pattern=command_pattern('start'))
        )
        self.bot.dispatcher.register_handler(self.on_start_callback, events.CallbackQuery)

    @pm_ban_check
    async def on_start_command(self, event: events.NewMessage.Event):
        try:
            user = await event.get_sender()

            user_buttons = [
                [Button.inline("Commands ❓", f"show_commands"), Button.url("Support 👨‍💻", "https://t.me/BotsUnion")],
                [Button.url("Repo 🛠️", "https://github.com/monsurcodes/telegram_assistant_bot")],
                [Button.url("Add Me To Your Group 🎉", "https://t.me/monsurbot?startgroup=new")],
            ]

            owner_buttons = [
                [Button.inline("Bot Stats 📊", f"bot_stats")],
                [Button.inline("All Commands ⚡", f"show_commands")],
            ]

            if int(user.id) == int(OWNER_ID):
                await event.reply(
                    OWNER_START_MESSAGE.format(user.first_name),
                    buttons=owner_buttons,
                    parse_mode="md"
                )
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
                await event.reply(
                    START_MESSAGE.format(user.first_name),
                    buttons=user_buttons,
                    parse_mode="md"
                )
        except Exception as e:
            logger.exception(e)
            await event.reply("Failed to send start message. Check bot logs for details.")

    @pm_ban_check
    async def on_start_callback(self, event: events.CallbackQuery.Event):
        data = event.data.decode()
        if data.startswith("show_commands"):
            await event.respond("Click /help to see the list of commands")
            await event.answer()
        elif data.startswith("bot_stats"):
            await event.respond("Click /stats to see system stats")
            await event.answer()