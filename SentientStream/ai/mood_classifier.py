"""
ai/mood_classifier.py
──────────────────────
Validates and normalises the raw dict returned by vision_analyzer.
Produces a clean record ready to insert into the video_moods table.
"""
from loguru import logger
from typing import Optional

VALID_MOODS = frozenset({
    "happy", "sad", "energetic", "calm",
    "romantic", "dark", "inspirational", "funny",
})


def _infer_primary(scores: dict) -> str:
    """Pick the highest-scoring valid mood from a scores dict."""
    valid = {k: v for k, v in scores.items() if k in VALID_MOODS}
    return max(valid, key=valid.get) if valid else "calm"


def _default(mood: str = "calm") -> dict:
    scores = {m: 0.0 for m in VALID_MOODS}
    scores[mood] = 1.0
    return {
        "primary_mood":      mood,
        "mood_scores":       scores,
        "scene_description": "",
        "analysis_text":     "",
        "model_used":        "default",
    }


def classify_mood(analysis: Optional[dict]) -> dict:
    """
    Takes the raw dict from vision_analyzer.analyze_video() and returns
    a normalised dict ready for DB insertion:
        {primary_mood, mood_scores (JSONB), scene_description,
         analysis_text, model_used}
    """
    if not analysis:
        return _default()

    # ── Validate primary_mood ──────────────────────────────────────────────
    primary = analysis.get("primary_mood", "").lower().strip()
    if primary not in VALID_MOODS:
        # try substring match
        matched = next((m for m in VALID_MOODS if m in primary), None)
        primary = matched or _infer_primary(analysis.get("mood_scores", {}))

    # ── Normalise mood_scores ──────────────────────────────────────────────
    raw_scores = analysis.get("mood_scores", {})
    scores: dict[str, float] = {}
    for mood in VALID_MOODS:
        try:
            val = float(raw_scores.get(mood, 0.0))
            scores[mood] = max(0.0, min(1.0, val))   # clamp to [0, 1]
        except (TypeError, ValueError):
            scores[mood] = 0.0

    total = sum(scores.values())
    if total > 0:
        scores = {k: round(v / total, 4) for k, v in scores.items()}
    else:
        scores[primary] = 1.0

    return {
        "primary_mood":      primary,
        "mood_scores":       scores,
        "scene_description": analysis.get("scene_description", ""),
        "analysis_text":     analysis.get("raw_response", ""),
        "model_used":        analysis.get("model_used", "unknown"),
    }
