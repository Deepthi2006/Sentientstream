"""
ingestion/downloader.py
───────────────────────
Downloads video files from Pexels CDN and persists metadata to PostgreSQL.
"""
import os
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import AsyncSessionLocal
from database.models.video import Video

STORAGE_DIR = os.getenv("STORAGE_DIR", "storage/videos")
Path(STORAGE_DIR).mkdir(parents=True, exist_ok=True)


# ─── helpers ──────────────────────────────────────────────────────────────────

async def _video_exists(session: AsyncSession, pexels_id: int) -> bool:
    result = await session.execute(
        select(Video).where(Video.pexels_id == pexels_id)
    )
    return result.scalar_one_or_none() is not None


async def _save_metadata(session: AsyncSession, data: dict) -> Video:
    """Insert a Video row with status='pending'."""
    video = Video(
        pexels_id=data["pexels_id"],
        title=data.get("title"),
        description=data.get("description"),
        duration=data.get("duration"),
        width=data.get("width"),
        height=data.get("height"),
        fps=data.get("fps"),
        thumbnail_url=data.get("thumbnail_url"),
        tags=data.get("tags", []),
        author=data.get("author"),
        source_url=data.get("source_url"),
        status="pending",
    )
    session.add(video)
    await session.commit()
    await session.refresh(video)
    return video


async def _download_file(session: AsyncSession, video: Video,
                          download_url: str) -> bool:
    """Download .mp4 from Pexels CDN → storage/videos/<pexels_id>.mp4"""
    filename  = f"{video.pexels_id}.mp4"
    file_path = os.path.join(STORAGE_DIR, filename)

    video.status = "downloading"
    await session.commit()

    try:
        timeout = aiohttp.ClientTimeout(total=300)
        async with aiohttp.ClientSession(timeout=timeout) as http:
            async with http.get(download_url) as resp:
                resp.raise_for_status()
                async with aiofiles.open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(512 * 1024):
                        await f.write(chunk)

        video.local_path = os.path.abspath(file_path)
        video.file_size  = os.path.getsize(file_path)
        video.status     = "downloaded"
        await session.commit()
        logger.success(f"  ✅ {filename} ({video.file_size // 1024} KB)")
        return True

    except Exception as exc:
        logger.error(f"  ❌ {filename}: {exc}")
        video.status = "failed"
        await session.commit()
        if os.path.exists(file_path):
            os.remove(file_path)
        return False


# ─── main entry ───────────────────────────────────────────────────────────────

async def download_all_videos(videos_metadata: list[dict]) -> dict:
    """
    Save metadata + download all videos.
    Returns stats: saved / downloaded / skipped / failed.
    """
    stats = {"saved": 0, "downloaded": 0, "skipped": 0, "failed": 0}

    logger.info(f"📥 Starting ingestion of {len(videos_metadata)} videos...")

    async with AsyncSessionLocal() as session:
        for i, data in enumerate(videos_metadata, 1):
            pid = data["pexels_id"]
            logger.info(f"[{i:>2}/{len(videos_metadata)}] pexels_id={pid}")

            if await _video_exists(session, pid):
                logger.info("  ⏭️  Already in DB, skipping")
                stats["skipped"] += 1
                continue

            video = await _save_metadata(session, data)
            stats["saved"] += 1

            url = data.get("download_url")
            if not url:
                logger.warning("  ⚠️  No download URL — marking failed")
                video.status = "failed"
                await session.commit()
                stats["failed"] += 1
                continue

            ok = await _download_file(session, video, url)
            stats["downloaded" if ok else "failed"] += 1

            await asyncio.sleep(0.5)   # be polite to the CDN

    logger.success(
        f"\n📊 Ingestion complete:\n"
        f"   ✅ Saved:      {stats['saved']}\n"
        f"   ✅ Downloaded: {stats['downloaded']}\n"
        f"   ⏭️  Skipped:   {stats['skipped']}\n"
        f"   ❌ Failed:     {stats['failed']}"
    )
    return stats
