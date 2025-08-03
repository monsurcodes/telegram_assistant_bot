from telethon import events

from bot.core.base_plugin import BasePlugin
from bot.db.crud.reddit_subscription_crud import RedditChatSettingsCRUD
from bot.db.db_session import db
from bot.middleware.pm_ban_check import pm_ban_check
from bot.middleware.register_command_help import register_help_text
from bot.services.reddit_dispatcher import RedditDispatcher
from bot.utils.command_patterns import args_command_pattern
from bot.utils.logger import get_logger

logger = get_logger(__name__)

chat_settings_crud = RedditChatSettingsCRUD(db)


class RedditMemeSubPlugin(BasePlugin):
    name = "RedditMemes"

    def register(self):
        self.bot.dispatcher.register_handler(
            self.subscribe_meme_cmd,
            events.NewMessage(pattern=args_command_pattern("subscribe_reddit"))
        )
        self.bot.dispatcher.register_handler(
            self.unsubscribe_meme_cmd,
            events.NewMessage(pattern=args_command_pattern("unsubscribe_reddit"))
        )
        self.bot.dispatcher.register_handler(
            self.unsubscribe_all_cmd,
            events.NewMessage(pattern=args_command_pattern("unsubscribe_reddit_all"))
        )
        self.bot.dispatcher.register_handler(
            self.list_subreddits_cmd,
            events.NewMessage(pattern=args_command_pattern("list_subreddits"))
        )
        if not hasattr(self.bot, "_reddit_dispatcher_started"):
            self.bot._reddit_dispatcher_started = True
            from asyncio import create_task
            reddit_dispatcher = RedditDispatcher(self.bot, chat_settings_crud)
            create_task(reddit_dispatcher.run())
        logger.info("RedditMemeSubPlugin registered [subscribe_reddit, unsubscribe_reddit, unsubscribe_reddit_all, list_subreddits] commands")

    @register_help_text(
        "/subscribe_reddit <chat_id?> <subreddit> <interval>",
        "Subscribe to Reddit memes! Usage:\n"
        "/subscribe_reddit dankmemes 15\n"
        "/subscribe_reddit -1001111 memes 20\n"
        "<interval> is in minutes.\n"
        "All subreddits subscribed to a chat share the same interval."
    )
    @pm_ban_check
    async def subscribe_meme_cmd(self, event: events.NewMessage.Event):
        args = event.pattern_match.group(1)
        if not args:
            await event.reply("Usage: /subscribe_reddit <chat_id?> <subreddit> <interval>")
            return

        vals = args.strip().split()
        if len(vals) < 2:
            await event.reply("Usage: /subscribe_reddit <chat_id?> <subreddit> <interval>")
            return

        if vals[0].startswith("-") or (vals[0].isdigit() and len(vals) == 3):
            if len(vals) != 3:
                await event.reply("Usage: /subscribe_reddit <chat_id> <subreddit> <interval>")
                return
            chat_id, subreddit, interval = vals
        else:
            chat_id, subreddit, interval = event.chat_id, vals[0], vals[1]

        try:
            chat_id = int(chat_id)
            interval = int(interval)
        except ValueError:
            await event.reply("Chat ID and interval should be numeric values.")
            return

        await chat_settings_crud.add_subreddit(chat_id, subreddit, interval)
        await event.reply(
            f"Subscribed to <b>r/{subreddit}</b> memes with interval <b>{interval} min</b> in chat <code>{chat_id}</code>!",
            parse_mode="html"
        )

    @register_help_text(
        "/unsubscribe_reddit <subreddit>",
        "Unsubscribe the current chat (or given chat_id) from the specified subreddit."
    )
    @pm_ban_check
    async def unsubscribe_meme_cmd(self, event: events.NewMessage.Event):
        args = event.pattern_match.group(1)
        if not args:
            await event.reply("Usage: /unsubscribe_reddit <subreddit>")
            return

        subreddit = args.strip().lower()
        chat_id = event.chat_id

        removed = await chat_settings_crud.remove_subreddit(chat_id, subreddit)
        if removed:
            await event.reply(f"Unsubscribed from <b>r/{subreddit}</b> memes in this chat.", parse_mode="html")
        else:
            await event.reply(f"You are not subscribed to <b>r/{subreddit}</b> in this chat.", parse_mode="html")

    @register_help_text(
        "/unsubscribe_reddit_all",
        "Unsubscribe the current chat from all subreddit meme subscriptions."
    )
    @pm_ban_check
    async def unsubscribe_all_cmd(self, event: events.NewMessage.Event):
        chat_id = event.chat_id
        removed = await chat_settings_crud.remove_all_subreddits(chat_id)
        if removed:
            await event.reply("All subreddit meme subscriptions have been removed from this chat.")
        else:
            await event.reply("No subreddit meme subscriptions found for this chat.")

    @register_help_text(
        "/list_subreddits",
        "List all subreddits currently subscribed for this chat."
    )
    @pm_ban_check
    async def list_subreddits_cmd(self, event: events.NewMessage.Event):
        chat_id = event.chat_id
        chat_settings = await chat_settings_crud.get_chat_settings(chat_id)

        if not chat_settings or not chat_settings.subreddits:
            await event.reply("🚫 This chat has no subscribed subreddits.")
            return

        interval = chat_settings.interval
        subreddits = chat_settings.subreddits

        subs_list = "\n".join(f"• <b>r/{sub}</b>" for sub in subreddits)
        message = (
            f"📢 <b>Subscribed subreddits for this chat:</b>\n\n"
            f"{subs_list}\n\n"
            f"⏰ Interval: <b>{interval} minutes</b> between posts"
        )

        await event.reply(message, parse_mode="html")
