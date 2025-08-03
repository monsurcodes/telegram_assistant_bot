from functools import wraps

from bot.db.crud.user_crud import UserCRUD
from bot.db.db_session import db

user_crud = UserCRUD(db)


def pm_ban_check(handler_func):
    @wraps(handler_func)
    async def wrapper(self, event, *args, **kwargs):
        user = await event.get_sender()

        user_record = await user_crud.get_user(user.id)
        if user_record and getattr(user_record, "is_pm_banned", False):
            await event.reply(
                "🚫 You are banned from using this bot.\nContact an admin if you think this is a mistake."
            )
            return
        return await handler_func(self, event, *args, **kwargs)

    return wrapper
