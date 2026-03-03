"""
scripts/run_ingestion.py
─────────────────────────
STEP 1 — Download 50 videos from Pexels and store metadata in PostgreSQL.

Usage:
    cd d:\aws\SentientStream
    python -m scripts.run_ingestion
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loguru import logger
from ingestion.pexels_client import fetch_all_videos
from ingestion.downloader import download_all_videos


async def main():
    logger.info("=" * 55)
    logger.info("  SentientStream — Step 1: Video Ingestion")
    logger.info("=" * 55)

    # 1. Fetch metadata from Pexels API
    videos_metadata = fetch_all_videos(total=50)

    if not videos_metadata:
        logger.error("No videos returned from Pexels. Check your API key.")
        return

    # 2. Download files + persist to PostgreSQL
    stats = await download_all_videos(videos_metadata)

    logger.info("\n✅ Ingestion complete. Next step:")
    logger.info("   python -m scripts.run_ai_pipeline")


if __name__ == "__main__":
    asyncio.run(main())
