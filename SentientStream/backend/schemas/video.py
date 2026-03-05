"""
backend/schemas/video.py
─────────────────────────
Pydantic response models for the API.
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MoodScores(BaseModel):
    happy:         float = 0.0
    sad:           float = 0.0
    energetic:     float = 0.0
    calm:          float = 0.0
    romantic:      float = 0.0
    dark:          float = 0.0
    inspirational: float = 0.0
    funny:         float = 0.0


class VideoMoodOut(BaseModel):
    primary_mood:      str
    mood_scores:       Optional[MoodScores] = None
    scene_description: Optional[str]        = None

    model_config = {"from_attributes": True}


class VideoOut(BaseModel):
    id:            uuid.UUID
    pexels_id:     Optional[int] = None
    title:         Optional[str]
    description:   Optional[str]
    duration:      Optional[int]
    width:         Optional[int]
    height:        Optional[int]
    thumbnail_url: Optional[str]
    author:        Optional[str]
    tags:          Optional[list[str]]
    status:        str
    mood:          Optional[VideoMoodOut] = None
    stream_url:    Optional[str]         = None
    created_at:    datetime

    model_config = {"from_attributes": True}


class FeedItem(BaseModel):
    video_id:      uuid.UUID
    stream_url:    str
    thumbnail_url: Optional[str]
    title:         Optional[str]
    duration:      Optional[int]
    primary_mood:  str
    score:         float          # cosine similarity score from FAISS
