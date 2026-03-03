"""
ingestion/pexels_client.py
──────────────────────────
Fetches video metadata from the Pexels API across 8 mood categories.
Returns structured dicts ready for downloading + DB insertion.
"""
import os
import httpx
from dotenv import load_dotenv
from loguru import logger
from typing import Optional

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
BASE_URL = "https://api.pexels.com/videos"

# Mood-to-search-query mapping
MOOD_QUERIES: dict[str, list[str]] = {
    "happy":         ["happy people celebration", "joy laughter fun"],
    "sad":           ["sad rain quiet", "lonely melancholy"],
    "energetic":     ["extreme sports fitness", "dance energy workout"],
    "calm":          ["nature peaceful ocean", "meditation relaxing"],
    "romantic":      ["couple love sunset", "romance candlelight"],
    "dark":          ["night city mystery", "dark dramatic fog"],
    "inspirational": ["mountain sunrise success", "achievement motivation"],
    "funny":         ["funny animals playful", "comedy humor"],
}

VIDEOS_PER_MOOD = 7   # 7 × 8 = 56 → trimmed to 50


def _headers() -> dict:
    return {"Authorization": PEXELS_API_KEY}


def _search(query: str, per_page: int = 10, page: int = 1) -> list[dict]:
    """Hit Pexels search endpoint and return raw video list."""
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(
                f"{BASE_URL}/search",
                headers=_headers(),
                params={
                    "query": query,
                    "per_page": per_page,
                    "page": page,
                    "orientation": "portrait",
                    "size": "medium",
                },
            )
            resp.raise_for_status()
            return resp.json().get("videos", [])
    except Exception as exc:
        logger.error(f"Pexels search failed for '{query}': {exc}")
        return []


def _best_mp4(video: dict) -> Optional[dict]:
    """Pick the best MP4 file: 480–1280px wide, highest resolution."""
    files = [
        f for f in video.get("video_files", [])
        if f.get("file_type") == "video/mp4"
        and 480 <= f.get("width", 0) <= 1280
    ]
    if not files:
        files = [f for f in video.get("video_files", [])
                 if f.get("file_type") == "video/mp4"]
    if not files:
        return None
    return max(files, key=lambda f: f.get("width", 0))


def fetch_all_videos(total: int = 50) -> list[dict]:
    """
    Fetch `total` videos from Pexels, distributed across all mood categories.
    Returns a list of structured dicts with download_url included.
    """
    all_videos: list[dict] = []
    seen_ids: set[int] = set()

    logger.info(f"🎬 Fetching {total} videos from Pexels across 8 moods...")

    for mood, queries in MOOD_QUERIES.items():
        mood_batch: list[dict] = []

        for query in queries:
            if len(mood_batch) >= VIDEOS_PER_MOOD:
                break
            results = _search(query, per_page=10, page=2)

            for v in results:
                if len(mood_batch) >= VIDEOS_PER_MOOD:
                    break
                vid_id: int = v["id"]
                if vid_id in seen_ids:
                    continue
                best = _best_mp4(v)
                if not best:
                    continue

                seen_ids.add(vid_id)
                mood_batch.append({
                    "pexels_id":    vid_id,
                    "title":        f"{mood.capitalize()} — {query}",
                    "description":  f"A {mood} video about {query}.",
                    "duration":     v.get("duration", 0),
                    "width":        best.get("width", v.get("width", 0)),
                    "height":       best.get("height", v.get("height", 0)),
                    "fps":          best.get("fps", 30.0),
                    "thumbnail_url": v.get("image", ""),
                    "tags":         [mood, *query.split()],
                    "author":       v.get("user", {}).get("name", "Unknown"),
                    "source_url":   v.get("url", ""),
                    "download_url": best.get("link", ""),
                    "search_mood":  mood,
                })

        all_videos.extend(mood_batch)
        logger.info(f"  {mood:>14}: {len(mood_batch)} videos")

        if len(all_videos) >= total:
            break

    result = all_videos[:total]
    logger.success(f"✅ Total fetched: {len(result)} videos")
    return result
