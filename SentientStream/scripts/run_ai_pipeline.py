"""
scripts/run_ai_pipeline.py
───────────────────────────
STEP 2 — Run AI mood analysis on all downloaded videos.
Extracts frames → Groq vision → mood classification → saves to video_moods table.

Usage:
    cd d:\aws\SentientStream
    python -m scripts.run_ai_pipeline
"""
import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.connection import AsyncSessionLocal
from database.models.video import Video
from database.models.mood import VideoMood
from ai.vision_analyzer import analyze_video
from ai.mood_classifier import classify_mood


async def get_unprocessed_videos() -> list[Video]:
    """Fetch all 'downloaded' videos that don't have a mood record yet."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Video)
            .outerjoin(VideoMood, VideoMood.video_id == Video.id)
            .where(
                Video.status == "downloaded",
                VideoMood.id.is_(None),
                Video.local_path.isnot(None),
            )
        )
        return list(result.scalars().all())


async def process_video(video: Video) -> bool:
    """Analyze one video and save mood to DB."""
    logger.info(f"\n🎬 [{video.pexels_id}] {video.title}")

    # Groq vision analysis (sync call — run in thread pool)
    loop    = asyncio.get_event_loop()
    raw     = await loop.run_in_executor(
        None, analyze_video, video.local_path, video.title or ""
    )

    # Normalize + validate
    mood_data = classify_mood(raw)
    logger.info(
        f"  🎭 Mood: {mood_data['primary_mood']} | "
        f"scene: {mood_data['scene_description'][:60]}..."
    )

    # Persist to DB
    async with AsyncSessionLocal() as session:
        # Re-fetch video in this session
        result = await session.execute(select(Video).where(Video.id == video.id))
        v = result.scalar_one()

        mood_rec = VideoMood(
            video_id          = v.id,
            primary_mood      = mood_data["primary_mood"],
            mood_scores       = mood_data["mood_scores"],
            scene_description = mood_data["scene_description"],
            analysis_text     = mood_data["analysis_text"],
            model_used        = mood_data["model_used"],
        )
        session.add(mood_rec)
        v.status = "processing"
        await session.commit()

    return True


async def main():
    logger.info("=" * 55)
    logger.info("  SentientStream — Step 2: AI Mood Analysis")
    logger.info("=" * 55)

    videos = await get_unprocessed_videos()
    logger.info(f"📋 Videos to process: {len(videos)}")

    if not videos:
        logger.warning("No downloaded videos found. Run step 1 first.")
        return

    success = failed = 0
    for i, video in enumerate(videos, 1):
        logger.info(f"\n[{i}/{len(videos)}]")
        try:
            ok = await process_video(video)
            if ok:
                success += 1
            else:
                failed += 1
        except Exception as exc:
            logger.error(f"  ❌ Error: {exc}")
            failed += 1

        # Respect Groq rate limits — ~2 req/sec on free tier
        if i < len(videos):
            time.sleep(2)

    logger.success(
        f"\n📊 AI pipeline done: {success} succeeded, {failed} failed\n"
        f"Next step: python -m scripts.run_indexer"
    )


if __name__ == "__main__":
    asyncio.run(main())
