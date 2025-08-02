from functools import wraps
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.tl.types import User
from bot.config import OWNER_ID
from bot.utils.logger import get_logger

logger = get_logger(__name__)

def group_admin_only(handler_func):
    @wraps(handler_func)
    async def wrapper(self, event, *args, **kwargs):
        sender = await event.get_sender()
        sender_id = int(sender.id)

        group = await self.bot.client.get_entity(event.chat_id)
        if not isinstance(group, User) and hasattr(group, 'id') and (getattr(group, 'megagroup', False) or getattr(group, 'broadcast', False)):
            try:
                if sender_id == int(OWNER_ID):
                    return await handler_func(self, event, *args, **kwargs)

                participants = await self.bot.client.get_participants(group, filter=ChannelParticipantsAdmins)
                admin_ids = [participant.id for participant in participants]
                if sender_id in set(admin_ids):
                    return await handler_func(self, event, *args, **kwargs)
                else:
                    await event.reply("Unauthorized: Only a group admin can use this command.")
            except Exception as e:
                logger.exception(e)
                await event.reply("Unauthorized: Unable to check your admin status.")
            return

        await event.reply("This command can only be used in groups owned by you or if you are an admin.")

    return wrapper
