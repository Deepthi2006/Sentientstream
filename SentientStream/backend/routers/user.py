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

from sqlalchemy import cast, Integer

@router.get("/insights")
async def get_user_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Daily breakdown (mocked based on all-time for simplicity, or we can use raw interactions)
    mood_result = await db.execute(
        select(
            VideoMood.primary_mood,
            func.coalesce(func.sum(Interaction.watch_duration), 0).label("watch_time")
        )
        .select_from(Interaction)
        .join(VideoMood, VideoMood.video_id == Interaction.video_id)
        .where(Interaction.user_id == current_user.id)
        .group_by(VideoMood.primary_mood)
        .order_by(desc("watch_time"))
    )
    
    mood_data = [{"mood": row.primary_mood, "watch_time": row.watch_time} for row in mood_result.all()]
    
    # Engagement stats
    eng_res = await db.execute(
        select(
            func.count(Interaction.id).label("total_plays"),
            func.sum(cast(Interaction.is_liked, Integer)).label("total_likes"),
            func.sum(cast(Interaction.replayed, Integer)).label("total_replays"),
        )
        .where(Interaction.user_id == current_user.id)
    )
    eng_stats = eng_res.first()

    return {
        "mood_distribution": mood_data,
        "engagement": {
            "total_plays": eng_stats.total_plays or 0,
            "total_likes": eng_stats.total_likes or 0,
            "total_replays": eng_stats.total_replays or 0,
        }
    }

@router.get("/weekly-summary")
async def get_weekly_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # A generated semantic summary of their behavioral data
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
    
    moods = mood_result.all()
    if not moods:
        return {
            "title": "Welcome to SentientStream!",
            "content": "You haven't watched enough videos yet for us to build your weekly emotional summary. Go watch some videos and come back later!",
            "dominant_mood": "Unknown",
            "suggestion": "Keep scrolling the Auto feed to calibrate your matrix."
        }

    dominant = moods[0].primary_mood
    mood_stats_str = ", ".join([f"{m.primary_mood} ({m.mood_count} videos)" for m in moods])

    try:
        import os
        from groq import AsyncGroq
        import logging
        
        client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"""You are the SentientStream AI algorithm. Write a highly personalized, slightly sci-fi/cyberpunk style paragraph (3 sentences max) analyzing the user's weekly video viewing habits. 
Their video mood stats are: {mood_stats_str}. Their dominant mood is {dominant}.
Explain what this means for their current emotional vector or 'neural matrix'. Be insightful, slick, and slightly mysterious as if you are a sentient machine curating their life. Return ONLY the paragraph (no markdown, no quotes, no extra text)."""
        
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        content = response.choices[0].message.content.strip().replace('"', '')
    except Exception as e:
        logging.getLogger("uvicorn").error(f"Groq API error for weekly summary: {e}")
        content = f"Your network displays strong {dominant} tendencies. Your emotional vectors are highly blended this week, showing a balanced and diverse watch history."

    return {
        "title": f"Your Weekly Vibe: {dominant.capitalize()}",
        "content": content,
        "dominant_mood": dominant,
        "suggestion": f"Currently optimizing your neural matrix for {dominant} resonance."
    }
