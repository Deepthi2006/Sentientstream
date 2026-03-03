from pydantic import BaseModel
import uuid
from datetime import datetime

class InteractionCreate(BaseModel):
    video_id: str
    watch_duration: int = 0
    is_liked: bool = False
    replayed: bool = False
    paused_count: int = 0

class InteractionOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    video_id: uuid.UUID
    watch_duration: int
    is_liked: bool
    replayed: bool
    paused_count: int
    created_at: datetime
    model_config = {"from_attributes": True}
