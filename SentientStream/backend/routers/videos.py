"""
backend/routers/videos.py
──────────────────────────
GET /videos          — list all ready videos
GET /videos/{id}     — single video detail
GET /videos/{id}/stream — byte-range aware video streaming
"""
import os
import re
from typing import Optional

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.connection import get_db
from database.models.video import Video
from backend.schemas.video import VideoOut

router = APIRouter(prefix="/videos", tags=["videos"])

CHUNK = 1024 * 1024   # 1 MB


def _stream_url(req: Request, video_id: str) -> str:
    return str(req.base_url) + f"videos/{video_id}/stream"


# ─── List all ready videos ───────────────────────────────────────────────────

@router.get("/", response_model=list[VideoOut])
async def list_videos(
    request: Request,
    mood:    Optional[str] = None,
    limit:   int           = 20,
    offset:  int           = 0,
    db:      AsyncSession  = Depends(get_db),
):
    stmt = (
        select(Video)
        .options(selectinload(Video.mood))
        .where(Video.status == "ready")
        .offset(offset)
        .limit(limit)
    )
    if mood:
        from database.models.mood import VideoMood
        stmt = (
            select(Video)
            .join(VideoMood, VideoMood.video_id == Video.id)
            .options(selectinload(Video.mood))
            .where(Video.status == "ready", VideoMood.primary_mood == mood)
            .offset(offset)
            .limit(limit)
        )

    result = await db.execute(stmt)
    videos = result.scalars().all()

    out = []
    for v in videos:
        data = VideoOut.model_validate(v)
        data.stream_url = _stream_url(request, str(v.id))
        out.append(data)
    return out


# ─── Single video ─────────────────────────────────────────────────────────────

@router.get("/{video_id}", response_model=VideoOut)
async def get_video(
    video_id: str,
    request:  Request,
    db:       AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Video)
        .options(selectinload(Video.mood))
        .where(Video.id == video_id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(404, "Video not found")

    data = VideoOut.model_validate(video)
    data.stream_url = _stream_url(request, video_id)
    return data


# ─── Video streaming with byte-range support ──────────────────────────────────

@router.get("/{video_id}/stream")
async def stream_video(video_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video  = result.scalar_one_or_none()

    if not video or not video.local_path:
        raise HTTPException(404, "Video file not found")
    if not os.path.exists(video.local_path):
        raise HTTPException(410, "Video file missing on disk")

    from fastapi.responses import FileResponse
    return FileResponse(
        video.local_path, 
        media_type="video/mp4", 
        headers={"Accept-Ranges": "bytes"}
    )
