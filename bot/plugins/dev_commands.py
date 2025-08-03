import platform
import sys

import psutil
from telethon import __version__ as telethon_version
from telethon import events

from bot.core.base_plugin import BasePlugin
from bot.db.crud.user_crud import UserCRUD
from bot.db.db_session import db
from bot.middleware.owner_check import owner_only
from bot.middleware.register_command_help import register_help_text
from bot.utils.command_patterns import command_pattern, args_command_pattern
from bot.utils.logger import get_logger

logger = get_logger(__name__)
user_crud = UserCRUD(db)


class DevPlugin(BasePlugin):
    name = "Dev"

    def register(self):
        self.bot.dispatcher.register_handler(self.ban_user_from_pm,
                                             events.NewMessage(pattern=args_command_pattern("ban_pm")))
        self.bot.dispatcher.register_handler(self.unban_user_from_pm,
                                             events.NewMessage(pattern=args_command_pattern("unban_pm")))
        self.bot.dispatcher.register_handler(self.on_sendlogs_command,
                                             events.NewMessage(pattern=command_pattern('getlogs')))
        self.bot.dispatcher.register_handler(self.stats_command,
                                             events.NewMessage(pattern=command_pattern("stats")))
        logger.info("DevPlugin registered [ban_pm, unban_pm, getlogs, stats] commands")

    @owner_only
    @register_help_text(
        "/ban_pm <username|user_id>",
        "Bans the specified user from using this bot privately."
        "Usage:\n- Reply to user's message in group with /ban_pm\n- Or /ban_pm <username or user_id>"
    )
    async def ban_user_from_pm(self, event: events.NewMessage.Event):
        user_to_ban_id = None

        if event.is_reply:
            # Ban the user who sent the replied message
            replied_msg = await event.get_reply_message()
            if replied_msg and replied_msg.sender_id:
                user_to_ban_id = replied_msg.sender_id
                logger.info(f"Ban via reply: user_id={user_to_ban_id}")
            else:
                await event.reply("Cannot determine the user to ban via reply.")
                return
        else:
            # Ban user by argument (username or numeric user_id)
            arg = event.pattern_match.group(1)
            if not arg:
                await event.reply("Please reply to a user or specify a username or user ID.")
                return
            arg = arg.strip()
            logger.info(f"Ban via argument: {arg}")

            if arg.isdigit():
                user_to_ban_id = int(arg)
            else:
                arg_username = arg.lstrip("@").lower()
                user_record = await user_crud.get_user_by_username(arg_username)
                if user_record:
                    user_to_ban_id = user_record.id  # You use alias _id = id in model
                else:
                    await event.reply(f"User with username @{arg_username} not found in database.")
                    return

        if user_to_ban_id is None:
            await event.reply("Could not determine user to ban.")
            return

        # Update user's 'is_pm_banned' flag to True using UserCRUD
        updated_user = await user_crud.update_user(user_to_ban_id, {"is_pm_banned": True})

        if updated_user:
            await event.reply(f"User with ID `{user_to_ban_id}` has been banned from using private messages.")
            logger.info(f"User {user_to_ban_id} banned from PM use by owner.")
        else:
            await event.reply(f"No user with ID `{user_to_ban_id}` was found or was already banned.")
            logger.warning(f"Tried banning user {user_to_ban_id} but no document was updated.")

    @owner_only
    @register_help_text(
        "/unban_pm <username|user_id>",
        "Unbans the specified user to allow usage of this bot privately."
        "Usage:\n- Reply to user's message in group with /unban_pm- Or /unban_pm <username or user_id>"
    )
    async def unban_user_from_pm(self, event: events.NewMessage.Event):
        user_to_unban_id = None

        if event.is_reply:
            replied_msg = await event.get_reply_message()
            if replied_msg and replied_msg.sender_id:
                user_to_unban_id = replied_msg.sender_id
            else:
                await event.reply("Cannot determine the user to unban via reply.")
                return
        else:
            arg = event.pattern_match.group(1)
            if not arg:
                await event.reply("Please reply to a user or specify a username or user ID.")
                return
            arg = arg.strip()

            if arg.isdigit():
                user_to_unban_id = int(arg)
            else:
                arg_username = arg.lstrip("@").lower()
                user_record = await user_crud.get_user_by_username(arg_username)
                if user_record:
                    user_to_unban_id = user_record.id
                else:
                    await event.reply(f"User with username @{arg_username} not found in database.")
                    return

        if user_to_unban_id is None:
            await event.reply("Could not determine user to unban.")
            return

        updated_user = await user_crud.update_user(user_to_unban_id, {"is_pm_banned": False})
        if updated_user:
            await event.reply(
                f"User with ID `{user_to_unban_id}` has been unbanned and can now use private messages.")
            logger.info(f"User {user_to_unban_id} unbanned from PM use by owner.")
        else:
            await event.reply(f"No user with ID `{user_to_unban_id}` was found or was not banned.")

    @owner_only
    @register_help_text(
        "/getlogs",
        "Sends bot logs to developer."
    )
    async def on_sendlogs_command(self, event: events.NewMessage.Event):
        try:
            user = await event.get_sender()

            await self.bot.client.send_file(
                user.id,
                file="logs/bot.log",
                caption="Bot logs!"
            )

            await event.reply(f"Sent log to {user.first_name}!")
        except Exception as e:
            logger.exception(e)
            await event.reply("Failed to send logs. Check bot logs for details.")

    @owner_only
    @register_help_text(
        "/stats",
        "Show statistics: Telethon and Python version, system info, RAM, CPU, and number of users."
    )
    async def stats_command(self, event: events.NewMessage.Event):
        try:
            # Get system info
            tele_version = telethon_version
            python_version = sys.version.split()[0]
            platform_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
            ram = psutil.virtual_memory()
            ram_used_mb = ram.used // (1024 * 1024)
            ram_total_mb = ram.total // (1024 * 1024)
            ram_percent = ram.percent
            cpu_percent = psutil.cpu_percent(interval=0.5)

            # Count users in db
            users_count = await user_crud.collection.count_documents({})

            text = (
                "📊 **Bot Stats:**\n\n"
                f"🤖 **Telethon:** `{tele_version}`\n"
                f"🐍 **Python:** `{python_version}`\n"
                f"💻 **System:** `{platform_info}`\n"
                f"🧠 **RAM Usage:** `{ram_used_mb} MB` / `{ram_total_mb} MB` ({ram_percent}%)\n"
                f"🖥️ **CPU Usage:** `{cpu_percent}%`\n"
                f"👤 **Registered Users:** `{users_count}`"
            )

            await event.reply(text, parse_mode="md")
        except Exception as e:
            logger.exception(e)
            await event.reply("Failed to get stats. Check bot logs for details.")
