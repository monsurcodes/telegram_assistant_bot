from typing import Optional

from bot.db.models.reddit_subscription import RedditChatSettings


class RedditChatSettingsCRUD:
    def __init__(self, db):
        self.collection = db["reddit_chat_settings"]

    async def add_subreddit(self, chat_id: int, subreddit: str, interval: int):
        subreddit = subreddit.lower()
        doc = await self.collection.find_one({"chat_id": chat_id})
        if doc:
            if subreddit not in doc.get("subreddits", []):
                doc["subreddits"].append(subreddit)
            if doc.get("interval") != interval:
                doc["interval"] = interval
            await self.collection.update_one({"chat_id": chat_id}, {"$set": doc})
        else:
            new_doc = {
                "chat_id": chat_id,
                "interval": interval,
                "subreddits": [subreddit],
            }
            await self.collection.insert_one(new_doc)

    async def get_all_chats(self):
        cursor = self.collection.find()
        results = []
        async for doc in cursor:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            results.append(RedditChatSettings(**doc))
        return results

    async def get_chat_settings(self, chat_id: int) -> Optional[RedditChatSettings]:
        doc = await self.collection.find_one({"chat_id": chat_id})
        if doc:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            return RedditChatSettings(**doc)
        return None

    async def remove_subreddit(self, chat_id: int, subreddit: str):
        subreddit = subreddit.lower()
        doc = await self.collection.find_one({"chat_id": chat_id})
        if not doc:
            return False
        subreddits = doc.get("subreddits", [])
        if subreddit in subreddits:
            subreddits.remove(subreddit)
            if subreddits:
                await self.collection.update_one(
                    {"chat_id": chat_id},
                    {"$set": {"subreddits": subreddits}}
                )
            else:
                await self.collection.delete_one({"chat_id": chat_id})
            return True
        return False

    async def remove_all_subreddits(self, chat_id: int):
        result = await self.collection.delete_one({"chat_id": chat_id})
        return result.deleted_count > 0
