from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.connection import get_db
from database.models.user import User
from database.models.video import Video
from database.models.interaction import Interaction
from backend.schemas.interaction import InteractionCreate
from backend.auth_utils import get_current_user
from backend.recommendation import update_user_embedding
import uuid
import asyncio

router = APIRouter(prefix="/interactions", tags=["interactions"])

@router.post("/")
async def record_interaction(
    interaction_in: InteractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        video_uuid = uuid.UUID(interaction_in.video_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video_id format")

    # verify video exists
    video_res = await db.execute(select(Video).where(Video.id == video_uuid))
    if not video_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Video not found")

    result = await db.execute(
        select(Interaction)
        .where(
            Interaction.user_id == current_user.id,
            Interaction.video_id == video_uuid
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.watch_duration += interaction_in.watch_duration
        if interaction_in.is_liked:
            existing.is_liked = True
        if interaction_in.replayed:
            existing.replayed = True
        existing.paused_count += interaction_in.paused_count
    else:
        new_inter = Interaction(
            user_id=current_user.id,
            video_id=video_uuid,
            watch_duration=interaction_in.watch_duration,
            is_liked=interaction_in.is_liked,
            replayed=interaction_in.replayed,
            paused_count=interaction_in.paused_count
        )
        db.add(new_inter)

    await db.commit()
    
    # Update user embedding immediately before returning
    await update_user_embedding(current_user.id, db)
    
    return {"status": "success"}
