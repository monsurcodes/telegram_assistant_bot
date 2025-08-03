import asyncio
import time
from collections import defaultdict

from bot.services.reddit_memes import RedditMemeService


class RedditDispatcher:
    def __init__(self, bot, chat_settings_crud):
        self.bot = bot
        self.crud = chat_settings_crud
        self.last_sent = {}
        self.subreddit_indices = defaultdict(int)

    async def run(self):
        while True:
            try:
                chats = await self.crud.get_all_chats()
                now = time.time()

                for chat in chats:
                    chat_id = chat.chat_id
                    interval_sec = chat.interval * 60
                    last = self.last_sent.get(chat_id, 0)

                    if now - last >= interval_sec and chat.subreddits:
                        idx = self.subreddit_indices[chat_id] % len(chat.subreddits)
                        subreddit = chat.subreddits[idx]

                        await self.send_meme(chat_id, subreddit)

                        self.subreddit_indices[chat_id] = (idx + 1) % len(chat.subreddits)
                        self.last_sent[chat_id] = now

                await asyncio.sleep(5)
            except Exception as e:
                print(f"RedditDispatcher error: {e}")
                await asyncio.sleep(60)

    async def send_meme(self, chat_id, subreddit):
        meme = await RedditMemeService.fetch_meme(subreddit)
        if not meme:
            return
        caption = (
            f"🔥 <b>{meme['title']}</b>\n"
            f"Subreddit: <code>r/{subreddit}</code>\n"
            f"👍 {meme['ups']} | 👤 {meme['author']}\n"
            f"<a href='{meme['postLink']}'>Reddit Post</a>"
        )
        file_path = None
        try:
            file_path = await RedditMemeService.download_image(meme["url"])
            if file_path:
                await self.bot.client.send_file(
                    chat_id,
                    file=str(file_path),
                    caption=caption,
                    force_document=False,
                    parse_mode="html",
                    link_preview=False
                )
            else:
                await self.bot.client.send_message(
                    chat_id, f"{caption}\n{meme['url']}", parse_mode="html"
                )
        finally:
            if file_path and file_path.exists():
                file_path.unlink()
