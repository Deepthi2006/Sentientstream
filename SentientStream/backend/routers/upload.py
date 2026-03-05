import os
import uuid
import shutil
import asyncio
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from pathlib import Path

from database.connection import get_db
from database.models.video import Video
from database.models.mood import VideoMood
from database.models.embedding import VideoEmbedding
from backend.auth_utils import get_current_user
from database.models.user import User
from ai.vision_analyzer import analyze_video
from ai.mood_classifier import classify_mood
from vector_store.indexer import build_faiss_index

router = APIRouter(prefix="/upload", tags=["upload"])

STORAGE_DIR = os.getenv("STORAGE_DIR", "storage/videos")
Path(STORAGE_DIR).mkdir(parents=True, exist_ok=True)

@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    1. Save uploaded .mp4 to disk
    2. Record metadata in DB
    3. Run AI analysis (vision + mood)
    4. Index for FAISS
    """
    if not file.filename.lower().endswith(".mp4"):
        raise HTTPException(400, "Only .mp4 files are supported.")

    video_id = uuid.uuid4()
    filename = f"user_{video_id}.mp4"
    file_path = os.path.join(STORAGE_DIR, filename)

    logger.info(f"📤 Uploading video: {file.filename} -> {filename}")

    try:
        # 1. Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Database Record
        new_video = Video(
            id=video_id,
            pexels_id=None, # It's a user upload
            is_user_upload=1,
            title=file.filename,
            local_path=os.path.abspath(file_path),
            file_size=os.path.getsize(file_path),
            status="downloaded"
        )
        db.add(new_video)
        await db.commit()
        await db.refresh(new_video)

        # 3. AI Analysis
        # We run this inline for now, ideally it's a background task
        loop = asyncio.get_event_loop()
        raw_analysis = await loop.run_in_executor(
            None, analyze_video, new_video.local_path, new_video.title
        )
        
        if not raw_analysis:
            new_video.status = "failed"
            await db.commit()
            raise HTTPException(500, "AI Analysis failed for this video.")

        mood_data = classify_mood(raw_analysis)
        
        mood_rec = VideoMood(
            video_id=new_video.id,
            primary_mood=mood_data["primary_mood"],
            mood_scores=mood_data["mood_scores"],
            scene_description=mood_data["scene_description"],
            analysis_text=mood_data["analysis_text"],
            model_used=mood_data["model_used"]
        )
        db.add(mood_rec)
        new_video.status = "processing"
        await db.commit()

        # 4. Final Indexing
        # Re-run the indexer for un-indexed videos
        await build_faiss_index()

        return {
            "status": "success",
            "video_id": str(new_video.id),
            "mood": mood_data["primary_mood"]
        }

    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(500, f"Internal Server Error: {str(e)}")
