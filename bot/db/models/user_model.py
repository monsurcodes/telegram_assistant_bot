from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserPhoto(BaseModel):
    photo_id: Optional[int] = None
    dc_id: Optional[int] = None
    has_video: Optional[bool] = False

class User(BaseModel):
    id: int = Field(..., alias="_id")  # Use Telegram user ID as _id in MongoDB
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    access_hash: Optional[int] = None
    photo: Optional[UserPhoto] = None
    lang_code: Optional[str] = "en"
    is_pm_banned: Optional[bool] = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
