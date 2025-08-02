from telethon import events
from telethon.errors.rpcerrorlist import ChatAdminRequiredError, RightForbiddenError
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights

from bot.core.base_plugin import BasePlugin
from bot.middleware.group_admin import group_admin_only
from bot.middleware.register_command_help import register_help_text
from bot.utils.command_patterns import args_command_pattern
from bot.utils.logger import get_logger

logger = get_logger(__name__)


class AdminPlugin(BasePlugin):
    name = "Admin"

    def register(self):
        self.bot.dispatcher.register_handler(self.promote_user,
                                             events.NewMessage(pattern=args_command_pattern("promote")))
        self.bot.dispatcher.register_handler(self.demote_user,
                                             events.NewMessage(pattern=args_command_pattern("demote")))
        self.bot.dispatcher.register_handler(self.ban_user,
                                             events.NewMessage(pattern=args_command_pattern("ban")))
        self.bot.dispatcher.register_handler(self.unban_user,
                                             events.NewMessage(pattern=args_command_pattern("unban")))
        self.bot.dispatcher.register_handler(self.kick_user,
                                             events.NewMessage(pattern=args_command_pattern("kick")))
        logger.info("AdminPlugin registered [promote, demote, ban, unban, kick] commands.")

    @register_help_text(
        "/promote <user_id> [rank]",
        "Promote a user to group admin by replying to their message with /promote [rank] or by giving their user ID with optional rank."
    )
    @group_admin_only
    async def promote_user(self, event: events.NewMessage.Event):
        chat = await event.get_chat()

        user_id = None
        rank = None

        args_text = event.pattern_match.group(1) or ""
        args_parts = args_text.strip().split(maxsplit=1)

        if event.is_reply:
            reply_msg = await event.get_reply_message()
            if reply_msg and reply_msg.sender_id:
                user_id = reply_msg.sender_id
            else:
                await event.reply("Cannot find the user to promote in the replied message.")
                return

            if args_text.strip():
                rank = args_text.strip()
        else:
            if len(args_parts) == 0 or not args_parts[0].isdigit():
                await event.reply("Please reply to a user or provide a valid user ID to promote.")
                return
            user_id = int(args_parts[0])

            if len(args_parts) == 2:
                rank = args_parts[1].strip()

        if not rank:
            rank = "admin"

        try:
            await self.bot.client.edit_admin(
                chat.id,
                user_id,
                invite_users=True,
                ban_users=True,
                delete_messages=True,
                pin_messages=True,
                manage_call=True,
                title=rank,
            )
            await event.reply(f"User with ID `{user_id}` has been promoted to group admin with title '{rank}'.")
            logger.info(f"Promoted user {user_id} to admin with title '{rank}' in chat {chat.id}")

        except ChatAdminRequiredError as CARE:
            logger.error(
                f"Failed to promote user {user_id} to admin in chat {chat.id} due to lack of permissions.\n{CARE}"
            )
            await event.reply("I don't have permission to do that.")

        except RightForbiddenError as RFE:
            try:
                await self.bot.client(
                    EditAdminRequest(
                        channel=chat,
                        user_id=user_id,
                        admin_rights=ChatAdminRights(
                            change_info=True,
                            post_messages=True,
                            edit_messages=True,
                            delete_messages=True,
                            ban_users=True,
                            invite_users=True,
                            pin_messages=True,
                            add_admins=False,
                            manage_call=True,
                            other=True,
                        ),
                        rank=rank,
                    )
                )
                await event.reply(f"User with ID `{user_id}` has been promoted to group admin with title '{rank}'.")
                logger.info(f"Promoted user {user_id} to admin with title '{rank}' in chat {chat.id}")
            except Exception as err:
                logger.exception(f"Failed to promote user {user_id}.\n{err}")
                await event.reply(f"Failed to promote user {user_id}")
            logger.error(
                f"Failed to promote user {user_id} to admin in chat {chat.id}.\n{RFE}"
            )
            await event.reply("This command only works in groups with admin management (supergroups or channels).")

        except Exception as e:
            logger.exception(f"Failed to promote user {user_id}.\n{e}")
            await event.reply(f"Failed to promote user {user_id}")

    @register_help_text(
        "/demote <user_id>",
        "Demote a user from group admin by replying to their message with /demote or by giving their user ID."
    )
    @group_admin_only
    async def demote_user(self, event: events.NewMessage.Event):
        chat = await event.get_chat()

        user_id = None

        if event.is_reply:
            reply_msg = await event.get_reply_message()
            if reply_msg and reply_msg.sender_id:
                user_id = reply_msg.sender_id
            else:
                await event.reply("Cannot find the user to demote in the replied message.")
                return
        else:
            arg = event.pattern_match.group(1)
            if not arg or not arg.strip().isdigit():
                await event.reply("Please reply to a user or provide a valid user ID to demote.")
                return
            user_id = int(arg.strip())

        try:
            await self.bot.client.edit_admin(
                chat.id,
                user_id,
                invite_users=False,
                ban_users=False,
                delete_messages=False,
                pin_messages=False,
                manage_call=False,
                title="",
            )
            await event.reply(f"User with ID `{user_id}` has been demoted from admin.")
            logger.info(f"Demoted user {user_id} from admin in chat {chat.id}")

        except ChatAdminRequiredError as CARE:
            logger.error(f"Failed to demote user {user_id} in chat {chat.id} due to lack of permissions.\n{CARE}")
            await event.reply("I don't have permission to do that.")

        except RightForbiddenError as RFE:
            try:
                await self.bot.client(
                    EditAdminRequest(
                        channel=chat,
                        user_id=user_id,
                        admin_rights=ChatAdminRights(
                            change_info=False,
                            post_messages=False,
                            edit_messages=False,
                            delete_messages=False,
                            ban_users=False,
                            invite_users=False,
                            pin_messages=False,
                            add_admins=False,
                            manage_call=False,
                            other=False,
                        ),
                        rank="",
                    )
                )
                await event.reply(f"User with ID `{user_id}` has been demoted from admin.")
                logger.info(f"Demoted user {user_id} from admin in chat {chat.id}")
            except Exception as err:
                logger.exception(f"Failed to demote user {user_id}.\n{err}")
                await event.reply(f"Failed to demote user {user_id}")
            logger.error(f"Failed to demote user {user_id} in chat {chat.id}.\n{RFE}")
            await event.reply("This command only works in groups with admin management (supergroups or channels).")

        except Exception as e:
            logger.exception(f"Failed to demote user {user_id}.\n{e}")
            await event.reply(f"Failed to demote user {user_id}")

    @register_help_text(
        "/ban <user_id>",
        "Ban a user from the group by replying to their message with /ban or by giving their user ID."
    )
    @group_admin_only
    async def ban_user(self, event: events.NewMessage.Event):
        chat = await event.get_chat()

        user_id = None

        if event.is_reply:
            reply_msg = await event.get_reply_message()
            if reply_msg and reply_msg.sender_id:
                user_id = reply_msg.sender_id
            else:
                await event.reply("Cannot find the user to ban in the replied message.")
                return
        else:
            arg = event.pattern_match.group(1)
            if not arg or not arg.strip().isdigit():
                await event.reply("Please reply to a user or provide a valid user ID to ban.")
                return
            user_id = int(arg.strip())

        try:
            await self.bot.client.edit_permissions(
                chat.id,
                user_id,
                view_messages=False
            )
            await event.reply(f"User with ID `{user_id}` has been banned from the group.")
            logger.info(f"Banned user {user_id} from chat {chat.id}")

        except ChatAdminRequiredError as e:
            logger.error(f"Failed to ban user {user_id} in chat {chat.id} due to lack of permissions.\n{e}")
            await event.reply("I don't have permission to ban users.")

        except Exception as e:
            logger.exception(f"Failed to ban user {user_id}.\n{e}")
            await event.reply(f"Failed to ban user {user_id}.")

    @register_help_text(
        "/unban <user_id>",
        "Unban a user from the group by replying to their message with /unban or by giving their user ID."
    )
    @group_admin_only
    async def unban_user(self, event: events.NewMessage.Event):
        chat = await event.get_chat()

        user_id = None

        if event.is_reply:
            reply_msg = await event.get_reply_message()
            if reply_msg and reply_msg.sender_id:
                user_id = reply_msg.sender_id
            else:
                await event.reply("Cannot find the user to unban in the replied message.")
                return
        else:
            arg = event.pattern_match.group(1)
            if not arg or not arg.strip().isdigit():
                await event.reply("Please reply to a user or provide a valid user ID to unban.")
                return
            user_id = int(arg.strip())

        try:
            await self.bot.client.edit_permissions(
                chat.id,
                user_id,
                view_messages=True
            )
            await event.reply(f"User with ID `{user_id}` has been unbanned from the group.")
            logger.info(f"Unbanned user {user_id} from chat {chat.id}")

        except ChatAdminRequiredError as e:
            logger.error(f"Failed to unban user {user_id} in chat {chat.id} due to lack of permissions.\n{e}")
            await event.reply("I don't have permission to unban users.")

        except Exception as e:
            logger.exception(f"Failed to unban user {user_id}.\n{e}")
            await event.reply(f"Failed to unban user {user_id}.")

    @register_help_text(
        "/kick <user_id>",
        "Kick a user from the group by replying to their message with /kick or by giving their user ID."
    )
    @group_admin_only
    async def kick_user(self, event: events.NewMessage.Event):
        chat = await event.get_chat()

        user_id = None

        if event.is_reply:
            reply_msg = await event.get_reply_message()
            if reply_msg and reply_msg.sender_id:
                user_id = reply_msg.sender_id
            else:
                await event.reply("Cannot find the user to kick in the replied message.")
                return
        else:
            arg = event.pattern_match.group(1)
            if not arg or not arg.strip().isdigit():
                await event.reply("Please reply to a user or provide a valid user ID to kick.")
                return
            user_id = int(arg.strip())

        try:
            await self.bot.client.kick_participant(chat.id, user_id)
            await event.reply(f"User with ID `{user_id}` has been kicked from the group.")
            logger.info(f"Kicked user {user_id} from chat {chat.id}")

        except ChatAdminRequiredError as e:
            logger.error(f"Failed to kick user {user_id} in chat {chat.id} due to lack of permissions.\n{e}")
            await event.reply("I don't have permission to kick users.")

        except Exception as e:
            logger.exception(f"Failed to kick user {user_id}.\n{e}")
            await event.reply(f"Failed to kick user {user_id}.")
