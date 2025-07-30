from datetime import datetime
from typing import Optional, List

from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.db.models.user_model import User


class UserCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    async def create_user(self, user_data: dict) -> User:
        user = User(**user_data)
        now = datetime.now()
        update_data = user.model_dump(by_alias=True)

        update_data.pop("created_at", None)

        update_data["updated_at"] = now

        update_result = await self.collection.update_one(
            {"_id": user.id},
            {
                "$set": update_data,
                "$setOnInsert": {"created_at": now},
            },
            upsert=True
        )

        doc = await self.collection.find_one({"_id": user.id})
        return User.model_validate(doc)

    async def get_user(self, user_id: int) -> Optional[User]:
        doc = await self.collection.find_one({"_id": user_id})
        if doc:
            return User.model_validate(doc)
        return None

    async def update_user(self, user_id: int, update_data: dict) -> Optional[User]:
        update_data["updated_at"] = datetime.now()
        result = await self.collection.update_one(
            {"_id": user_id},
            {"$set": update_data},
            upsert=True
        )
        if result.modified_count:
            # Return the updated user
            return await self.get_user(user_id)
        return None

    async def delete_user(self, user_id: int) -> bool:
        result = await self.collection.delete_one({"_id": user_id})
        return result.deleted_count > 0

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        cursor = self.collection.find().skip(skip).limit(limit)
        users = []
        async for doc in cursor:
            users.append(User.model_validate(doc))
        return users
