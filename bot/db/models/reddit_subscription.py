from typing import Optional, List

from pydantic import BaseModel, Field


class RedditChatSettings(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    chat_id: int
    interval: int
    subreddits: List[str] = []

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
