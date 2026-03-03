"""
vector_store/embedder.py
─────────────────────────
Generates 384-dim sentence embeddings using sentence-transformers.
Runs 100% locally — no API key, no cost.
"""
from __future__ import annotations
import numpy as np
from loguru import logger
from typing import Optional

MODEL_NAME    = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Mood synonym map — enriches the embedding space so mood queries
# land close to mood-labelled videos even if titles differ.
MOOD_SYNONYMS: dict[str, str] = {
    "happy":         "happy joyful cheerful upbeat positive fun celebration",
    "sad":           "sad melancholy gloomy sorrowful depressed lonely quiet",
    "energetic":     "energetic active dynamic intense powerful fast exciting",
    "calm":          "calm peaceful serene tranquil relaxing soothing gentle",
    "romantic":      "romantic love affectionate tender intimate sweet couple",
    "dark":          "dark mysterious dramatic tense moody noir night",
    "inspirational": "inspirational motivating uplifting empowering hopeful achievement",
    "funny":         "funny humorous comical amusing playful light-hearted",
}

_model = None

def get_model():
    """Lazy-load: model is downloaded once and cached in memory."""
    from sentence_transformers import SentenceTransformer
    global _model
    if _model is None:
        logger.info(f"📦 Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
        logger.success(f"✅ Embedding model ready (dim={EMBEDDING_DIM})")
    return _model


def build_video_text(video_data: dict) -> str:
    """
    Construct the text string that will be embedded for a video.
    Combines title, description, tags, mood label and scene description.
    """
    parts: list[str] = []

    if video_data.get("title"):
        parts.append(video_data["title"])
    if video_data.get("description"):
        parts.append(video_data["description"])
    if video_data.get("tags"):
        tags = video_data["tags"]
        parts.append(" ".join(tags) if isinstance(tags, list) else str(tags))
    if video_data.get("primary_mood"):
        mood = video_data["primary_mood"]
        parts.append(f"mood: {mood}")
        if mood in MOOD_SYNONYMS:
            parts.append(MOOD_SYNONYMS[mood])
    if video_data.get("scene_description"):
        parts.append(video_data["scene_description"])

    return ". ".join(parts)


def generate_embedding(text: str) -> np.ndarray:
    """Return a normalised 384-dim float32 vector."""
    model = get_model()
    vec   = model.encode(text, normalize_embeddings=True, show_progress_bar=False)
    return vec.astype("float32")


_mood_cache = None

def embed_mood_query(mood: str) -> np.ndarray:
    """
    Embed a bare mood string (e.g. 'calm') for feed search.
    Reads from pre-generated vector cache to save 400MB RAM in live API.
    """
    global _mood_cache
    import json
    import os
    
    if _mood_cache is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, "vector_store", "data", "mood_vectors.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                _mood_cache = json.load(f)
        else:
            _mood_cache = {}

    mood = mood.lower() if mood else "calm"
    if mood in _mood_cache:
        return np.array(_mood_cache[mood], dtype="float32")
        
    # Fallback to actual NLP computation (requires 400MB+ RAM)
    text = MOOD_SYNONYMS.get(mood, mood)
    return generate_embedding(text)
