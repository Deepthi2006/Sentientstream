from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from database.connection import get_db
from database.models.user import User
from database.models.interaction import Interaction
from database.models.mood import VideoMood
from backend.schemas.user import UserProfileOut
from backend.auth_utils import get_current_user
from collections import defaultdict

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile", response_model=UserProfileOut)
async def get_user_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Calculate total interactions and watch time
    result = await db.execute(
        select(
            func.count(Interaction.id).label("total_interactions"),
            func.coalesce(func.sum(Interaction.watch_duration), 0).label("total_duration")
        ).where(Interaction.user_id == current_user.id)
    )
    stats = result.first()
    total_interactions = stats.total_interactions if stats else 0
    total_duration = stats.total_duration if stats else 0
    
    # Calculate mood interactions
    # Counting interactions by primary mood, could use sum of interaction duration but count works for frequency
    mood_result = await db.execute(
        select(
            VideoMood.primary_mood,
            func.count(Interaction.id).label("mood_count")
        )
        .select_from(Interaction)
        .join(VideoMood, VideoMood.video_id == Interaction.video_id)
        .where(Interaction.user_id == current_user.id)
        .group_by(VideoMood.primary_mood)
        .order_by(desc("mood_count"))
    )
    
    mood_rows = mood_result.all()
    
    most_watched_moods = {row.primary_mood: row.mood_count for row in mood_rows}
    dominant_mood = mood_rows[0].primary_mood if mood_rows else None

    return UserProfileOut(
        id=current_user.id,
        username=current_user.username,
        created_at=current_user.created_at,
        total_interactions_count=total_interactions,
        total_watch_time=total_duration,
        most_watched_video_moods=most_watched_moods,
        dominant_mood=dominant_mood
    )
