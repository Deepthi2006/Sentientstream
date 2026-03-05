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

    content = "Your emotional vectors are highly blended this week, showing a balanced and diverse watch history."

    import os
    import json
    import logging
    prompt = f"""You are the SentientStream AI algorithm. Write a highly personalized, slightly sci-fi/cyberpunk style paragraph (3 sentences max) analyzing the user's weekly video viewing habits. 
Their video mood stats are: {mood_stats_str}. Their dominant mood is {dominant}.
Explain what this means for their current emotional vector or 'neural matrix'. Be insightful, slick, and slightly mysterious as if you are a sentient machine curating their life. Return ONLY the paragraph (no markdown, no quotes, no extra text)."""

    try_groq = True

    # 1. Try AWS Bedrock 
    try:
        import boto3
        session = boto3.Session()
        if session.get_credentials() is not None:
            region = os.getenv("AWS_DEFAULT_REGION", session.region_name or "us-east-1")
            client = session.client('bedrock-runtime', region_name=region)
            
            response = client.invoke_model(
                modelId="anthropic.claude-3-haiku-20240307-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 200,
                    "temperature": 0.7,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            response_body = json.loads(response.get("body").read())
            content = response_body.get("content")[0].get("text").strip().replace('"', '')
            try_groq = False
    except Exception as e:
        logging.getLogger("uvicorn").error(f"AWS Bedrock summary failed or not configured: {e}, falling back to Groq")

    # 2. Fallback to Groq
    if try_groq:
        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
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

@router.get("/ai-coach")
async def get_ai_coach(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # A generated semantic coaching summary
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
            "title": "Welcome to the Matrix",
            "content": "I am your personal AI Coach. To give you elite guidance, I need you to interact with the feed first. Watch some streams, react, and I will analyze your neuro-profile.",
            "action": "Start watching to unlock your elite AI coaching.",
            "intensity": 0
        }

    dominant = moods[0].primary_mood
    mood_stats_str = ", ".join([f"{m.primary_mood} ({m.mood_count})" for m in moods])

    import os
    import json
    import logging
    prompt = f"""You are an elite, high-performance 'AI Coach' for a user inside an app called SentientStream. 
Their dominant mood state is currently: {dominant}. Their precise behavioral profile is: {mood_stats_str}.
Give them an elite, high-contrast, cyberpunk-style tactical breakdown of their current state and actionable advice on how to elevate or utilize their mood right now. Make it powerful, sleek, and motivating (max 3 sentences). Return ONLY the coaching text (no markdown, no greetings)."""

    try_groq = True
    content = f"Your mental vector is leaning {dominant}. Keep striving, keep pushing boundaries. Maintain focus on the feed to calibrate further."

    # 1. Try AWS Bedrock 
    try:
        import boto3
        session = boto3.Session()
        if session.get_credentials() is not None:
            region = os.getenv("AWS_DEFAULT_REGION", session.region_name or "us-east-1")
            client = session.client('bedrock-runtime', region_name=region)
            
            response = client.invoke_model(
                modelId="anthropic.claude-3-haiku-20240307-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 200,
                    "temperature": 0.8,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            response_body = json.loads(response.get("body").read())
            content = response_body.get("content")[0].get("text").strip().replace('"', '')
            try_groq = False
    except Exception as e:
        logging.getLogger("uvicorn").error(f"AWS Bedrock coach failed or not configured: {e}, falling back to Groq")

    # 2. Fallback to Groq
    if try_groq:
        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
            response = await client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.8,
                max_tokens=200
            )
            content = response.choices[0].message.content.strip().replace('"', '')
        except Exception as e:
            logging.getLogger("uvicorn").error(f"Groq API error for AI Coach: {e}")

    # Map dominant mood to an intensity percentage (visual flare)
    intensity_map = {
        "energetic": 95,
        "sad": 40,
        "dark": 85,
        "happy": 80,
        "calm": 35,
        "inspirational": 90,
        "funny": 70,
        "romantic": 60
    }
    intensity = intensity_map.get(dominant, 50)

    return {
        "title": f"TACTICAL STATE: {dominant.upper()}",
        "content": content,
        "action": f"System calibrated. Proceed with {dominant} momentum.",
        "intensity": intensity
    }

@router.get("/vault")
async def get_vault_reconstruction(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch top 3 historically dominant moods to create 'Memory Orbs'
    mood_result = await db.execute(
        select(
            VideoMood.primary_mood,
            func.count(Interaction.id).label("watch_count")
        )
        .select_from(Interaction)
        .join(VideoMood, VideoMood.video_id == Interaction.video_id)
        .where(Interaction.user_id == current_user.id)
        .group_by(VideoMood.primary_mood)
        .order_by(desc("watch_count"))
        .limit(3)
    )
    
    top_moods = mood_result.all()
    if not top_moods:
        return {"memories": []}

    from backend.ai_utils import generate_sentient_text
    import asyncio

    memories = []
    # Process concurrent AI calls
    tasks = []
    for m in top_moods:
        prompt = f"Write a cryptic, 1-sentence cinematic movie trailer line for a video collection with the mood: {m.primary_mood}. Focus on the user's emotional evolution."
        tasks.append(generate_sentient_text(prompt))
    
    summaries = await asyncio.gather(*tasks)

    for i, m in enumerate(top_moods):
        # Fetch up to 5 recent videos for this mood arc
        vid_res = await db.execute(
            select(Video.id)
            .join(VideoMood, VideoMood.video_id == Video.id)
            .join(Interaction, Interaction.video_id == Video.id)
            .where(Interaction.user_id == current_user.id, VideoMood.primary_mood == m.primary_mood)
            .order_by(desc(Interaction.created_at))
            .limit(5)
        )
        vid_ids = [str(vid) for vid in vid_res.scalars().all()]

        memories.append({
            "mood": m.primary_mood,
            "title": f"The {m.primary_mood.capitalize()} Arc",
            "summary": summaries[i],
            "intensity": min(100, m.watch_count * 15),
            "video_ids": vid_ids,
            "reconstructed_at": func.now()
        })

    return {"memories": memories}

@router.get("/nexus")
async def get_nexus_rooms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from backend.ai_utils import generate_sentient_text
    
    # Get user's dominant mood for context
    res = await db.execute(
        select(VideoMood.primary_mood)
        .join(Interaction, Interaction.video_id == VideoMood.video_id)
        .where(Interaction.user_id == current_user.id)
        .order_by(desc(Interaction.created_at))
        .limit(1)
    )
    user_mood = res.scalar() or "calm"

    # Generate room names based on user frequency
    prompt = f"Create 3 unique, futuristic, elitist names for virtual sync rooms matching the theme: {user_mood}. Return ONLY a comma-separated list of names."
    room_names_raw = await generate_sentient_text(prompt, max_tokens=30)
    room_names = [name.strip() for name in room_names_raw.split(',')][:3]
    
    # Fallback names
    if len(room_names) < 3:
        room_names = ["Neural Void", "Cipher Hub", "Data Spire"]

    rooms = []
    moods = ["calm", "energetic", "dark"] # Different frequencies
    for i, name in enumerate(room_names):
        rooms.append({
            "id": f"room-{i}",
            "name": name,
            "mood": moods[i % len(moods)],
            "active_users": 5 + (i * 12),
            "sync_level": 70 + (i * 7)
        })

    return {"rooms": rooms}
