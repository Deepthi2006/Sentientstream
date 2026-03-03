"""
database/init_db.py
───────────────────
Run this once to create all PostgreSQL tables.

Usage:
    python -m database.init_db
"""
import asyncio
from loguru import logger
from database.connection import engine, Base

# Import models so SQLAlchemy registers them with Base.metadata
from database.models import Video, VideoMood, VideoEmbedding  # noqa: F401


async def init_db() -> None:
    logger.info("🗄️  Connecting to PostgreSQL...")
    async with engine.begin() as conn:
        logger.info("📐 Creating tables: videos, video_moods, video_embeddings")
        await conn.run_sync(Base.metadata.create_all)
    logger.success("✅ Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
