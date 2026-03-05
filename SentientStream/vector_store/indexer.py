"""
vector_store/indexer.py
────────────────────────
Orchestrates embedding + FAISS indexing for all processed videos.
Reads 'ready' or 'downloaded' videos that have a mood but no embedding yet.
"""
import asyncio
import uuid
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import AsyncSessionLocal
from database.models.video import Video
from database.models.mood import VideoMood
from database.models.embedding import VideoEmbedding
from vector_store.embedder import build_video_text, generate_embedding, MODEL_NAME, EMBEDDING_DIM
from vector_store.faiss_store import FAISSStore


async def _get_videos_to_index(session: AsyncSession) -> list[tuple]:
    """Return (Video, VideoMood) pairs not yet indexed."""
    # Videos that have a mood but no embedding record
    result = await session.execute(
        select(Video, VideoMood)
        .join(VideoMood, VideoMood.video_id == Video.id)
        .outerjoin(VideoEmbedding, VideoEmbedding.video_id == Video.id)
        .where(VideoEmbedding.id.is_(None))
    )
    return result.all()


async def build_faiss_index() -> None:
    """
    Main entry point.
    1. Load (or create) the FAISS store
    2. Fetch all un-indexed videos with moods
    3. Embed each one and add to FAISS
    4. Save faiss_index_id back to PostgreSQL
    5. Persist FAISS to disk
    """
    store = FAISSStore.load()

    async with AsyncSessionLocal() as session:
        pairs = await _get_videos_to_index(session)
        logger.info(f"📐 Videos to index: {len(pairs)}")

        for video, mood_rec in pairs:
            # Build text for embedding
            video_data = {
                "title":             video.title,
                "description":       video.description,
                "tags":              video.tags or [],
                "primary_mood":      mood_rec.primary_mood,
                "scene_description": mood_rec.scene_description or "",
            }
            text = build_video_text(video_data)
            vec  = generate_embedding(text)

            # Add to FAISS
            faiss_id = store.add(vec, str(video.id), mood_rec.primary_mood)

            # Persist the mapping in PostgreSQL
            emb = VideoEmbedding(
                video_id        = video.id,
                faiss_index_id  = faiss_id,
                embedding_model = MODEL_NAME,
                embedding_dim   = EMBEDDING_DIM,
                embedded_text   = text,
            )
            session.add(emb)

            # Mark video as ready
            video.status = "ready"

            logger.success(
                f"  ✅ Indexed: {video.pexels_id or 'USER_UPLOAD'} | "
                f"mood={mood_rec.primary_mood} | faiss_id={faiss_id}"
            )

        await session.commit()

    store.save()
    logger.success(f"\n🗂️  FAISS index now contains {store.index.ntotal} vectors")
