"""
backend/routers/feed.py
────────────────────────
GET /feed?mood=calm&k=10

Uses FAISS semantic search to find videos matching the requested mood.
Returns a ranked list of FeedItems with stream URLs.
"""
from fastapi import APIRouter, HTTPException, Request, Depends, Header
from loguru import logger
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db

from vector_store.faiss_store import FAISSStore
from vector_store.embedder import embed_mood_query
from backend.schemas.video import FeedItem
from backend.auth_utils import get_current_user_optional

router = APIRouter(prefix="/feed", tags=["feed"])

VALID_MOODS = {
    "happy", "sad", "energetic", "calm",
    "romantic", "dark", "inspirational", "funny",
}

# ── Lazy-load FAISS store once at startup ──────────────────────────────────────
_store: FAISSStore | None = None


def get_store() -> FAISSStore:
    global _store
    if _store is None:
        _store = FAISSStore.load()
    return _store


@router.get("/", response_model=list[FeedItem])
async def get_feed(
    request: Request,
    mood:    str = None,
    mode:    str = None,
    seen:    str = None,
    k:       int = 10,
    db: AsyncSession = Depends(get_db),
    Authorization: str = Header(None)
):
    """
    Returns top-k videos matching the requested mood, ranked by
    cosine similarity in the FAISS embedding space.
    If mode=auto, dynamically uses user_embedding for personalized search.
    """
    store = get_store()
    if store.index.ntotal == 0:
        raise HTTPException(503, "FAISS index not built yet. Run scripts/run_indexer.py first.")

    user = await get_current_user_optional(Authorization, db)
    
    excluded_video_ids = set()
    if seen:
        excluded_video_ids.update(seen.split(","))

    if user:
        from database.models.interaction import Interaction
        watched_res = await db.execute(
            select(Interaction.video_id).where(Interaction.user_id == user.id)
        )
        excluded_video_ids = {str(vid) for vid in watched_res.scalars().all()}

    query_vec = None
    mood_filter = None

    # ── Chrono-Filter Logic ──
    # Automatically adjust search priorities based on user's current local time
    # This doesn't affect explicit mood requests, but shifts the 'Auto' mode or empty mood fallback
    from datetime import datetime
    current_hour = datetime.now().hour
    chrono_mood = None
    
    if 6 <= current_hour <= 9:
        chrono_mood = "inspirational"
        logger.info(f"⏳ Chrono-Filter Active: Morning mode. Biasing towards {chrono_mood}.")
    elif current_hour >= 22 or current_hour <= 2:
        chrono_mood = "calm"
        logger.info(f"⏳ Chrono-Filter Active: Night mode. Biasing towards {chrono_mood}.")

    if not mood and not mode:
        mood = chrono_mood
    # ─────────────────────────

    if mode == "auto" and user and user.user_embedding:
        import numpy as np
        logger.info(f"🔍 FAISS search: mode=auto personalized for user {user.id}")
        query_vec = np.array(user.user_embedding, dtype=np.float32)
        # Search without mood filter to get pure personalized recommendations
        results = store.search(query_vec, k=k, excluded_video_ids=excluded_video_ids)
    else:
        if not mood:
            mood = "calm" # Default fallback
            if user:
                from database.models.interaction import Interaction
                from database.models.mood import VideoMood
                res = await db.execute(
                    select(VideoMood.primary_mood)
                    .join(Interaction, Interaction.video_id == VideoMood.video_id)
                    .where(Interaction.user_id == user.id)
                    .order_by(desc(Interaction.created_at))
                    .limit(10)
                )
                moods = res.scalars().all()
                if moods:
                    from collections import Counter
                    mood = Counter(moods).most_common(1)[0][0]
                    logger.info(f"Dynamically calculated user mood: {mood}")

        mood = mood.lower().strip()
        if mood not in VALID_MOODS:
            raise HTTPException(
                400,
                f"Invalid mood '{mood}'. Choose from: {', '.join(sorted(VALID_MOODS))}"
            )
        
        logger.info(f"🔍 FAISS search: mood={mood} k={k}")
        query_vec = embed_mood_query(mood)
        mood_filter = mood
        # Strictly search ONLY within the requested mood
        results = store.search(query_vec, k=k, mood_filter=mood_filter, excluded_video_ids=excluded_video_ids)

    # ── Diversity Injection ──
    # Mix in ~20-30% random fresh content to avoid repetition
    import random
    
    current_result_vids = {r["video_id"] for r in results}
    num_random_needed = max(1, int(k * 0.3)) if len(results) >= (k * 0.7) else k
    
    candidate_metadata = [
        meta for meta in store.metadata 
        if meta["video_id"] not in excluded_video_ids and meta["video_id"] not in current_result_vids
    ]
    
    # If mood filter exists, restrict diversity to ONLY this specific mood.
    if mood_filter:
        candidate_metadata = [m for m in candidate_metadata if m.get("mood") == mood_filter]
        num_random_needed = min(num_random_needed, len(candidate_metadata))

    if candidate_metadata and num_random_needed > 0:
        random_selections = random.sample(candidate_metadata, num_random_needed)
        
        # Determine how many elements to safely remove from bottom
        # Ensures we never pop more items than we actually have
        items_to_pop = min(len(results), len(results) + len(random_selections) - k)
        while items_to_pop > 0 and len(results) > 0:
            results.pop()
            items_to_pop -= 1
        
        for r in random_selections:
            diversity_item = dict(r)
            diversity_item["score"] = -1.0 # Indicator for diverse/random content
            results.append(diversity_item)
            
    # Shuffle slightly to integrate diverse items seamlessly
    random.shuffle(results)
    
    # Safe slice to top K
    results = results[:k] if len(results) > k else results

    # ── Dead-End Fallback ──
    # If the user has literally watched everything matching this mood to completion,
    # the strict exclusion filters above will leave them with an empty array.
    # To prevent dead-ends, disregard the database exclusions and give them rewatch content!
    if not results:
        logger.warning(f"Feed query resulted in NO content! (likely exhausted). Falling back without exclusions.")
        # If they asked for a specific mood, ONLY fallback to that mood's rewatch content!
        results = store.search(query_vec, k=k, mood_filter=mood_filter, excluded_video_ids=set())
        
        # Only fallback to absolute randomness if it's Auto mode (mood_filter is None)
        if not results and not mood_filter:
            results = store.search(query_vec, k=k, excluded_video_ids=set())
    
    # ── Logging ──
    user_log_id = user.id if user else "anonymous"
    rec_log_vids = [r["video_id"] for r in results]
    rec_log_scores = [round(r.get("score", 0.0), 4) for r in results]
    logger.info(f"Recommendation Log | User: {user_log_id} | Mode: {mode or 'mood'} | Vids: {rec_log_vids} | Scores: {rec_log_scores}")

    # We need video metadata — import here to avoid circular imports
    from database.connection import AsyncSessionLocal
    from database.models.video import Video
    from database.models.mood import VideoMood
    from sqlalchemy.orm import selectinload
    import uuid as _uuid

    video_ids = [_uuid.UUID(r["video_id"]) for r in results]
    score_map = {r["video_id"]: r["score"] for r in results}

    feed_items: list[FeedItem] = []

    async with AsyncSessionLocal() as db:
        db_result = await db.execute(
            select(Video)
            .options(selectinload(Video.mood))
            .where(Video.id.in_(video_ids))
        )
        videos = {str(v.id): v for v in db_result.scalars().all()}

    base = str(request.base_url)
    for r in results:
        vid = videos.get(r["video_id"])
        if not vid:
            continue
        feed_items.append(FeedItem(
            video_id      = vid.id,
            stream_url    = f"{base}videos/{vid.id}/stream",
            thumbnail_url = vid.thumbnail_url,
            title         = vid.title,
            duration      = vid.duration,
            primary_mood  = r["mood"],
            score         = score_map[r["video_id"]],
        ))

    return feed_items
