from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    created_at: datetime
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

class UserProfileOut(BaseModel):
    id: uuid.UUID
    username: str
    dominant_mood: Optional[str] = None
    total_watch_time: int = 0
    total_interactions_count: int = 0
    most_watched_video_moods: dict[str, int] = {}
    created_at: datetime
    model_config = {"from_attributes": True}
