"""
ai/vision_analyzer.py
──────────────────────
Sends video frames to Groq's vision model and gets mood analysis back.
Uses llama-3.2-11b-vision-preview — free on Groq's tier.
"""
import os
import json
import re
from typing import Optional

from groq import Groq
from dotenv import load_dotenv
from loguru import logger

from ai.frame_extractor import extract_key_frames, frames_to_base64

load_dotenv(override=True)

# Read model dynamically inside function — avoids module-level caching issues
def _get_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def _get_model():
    return os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

PROMPT = """You are a video mood analyst. Look at these video frames carefully.

Respond with ONLY valid JSON — no markdown fences, no extra text:
{
    "primary_mood": "<one of: happy | sad | energetic | calm | romantic | dark | inspirational | funny>",
    "mood_scores": {
        "happy": 0.0,
        "sad": 0.0,
        "energetic": 0.0,
        "calm": 0.0,
        "romantic": 0.0,
        "dark": 0.0,
        "inspirational": 0.0,
        "funny": 0.0
    },
    "scene_description": "1-2 sentences describing what you see",
    "reasoning": "why you chose this primary mood"
}

Rules:
- mood_scores values must sum to ~1.0
- primary_mood must be the key with the highest score
- Base your answer purely on visual content"""


def _extract_json(text: str) -> Optional[dict]:
    """Try several strategies to parse JSON from model output."""
    # 1. Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 2. Strip markdown code fences
    m = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # 3. First { ... } block
    m = re.search(r"\{[\s\S]+\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return None


def analyze_video(video_path: str, title: str = "") -> Optional[dict]:
    """
    Analyze a downloaded video file.

    Steps:
        1. Extract 3 key frames with OpenCV
        2. Base64-encode them
        3. Send to Groq vision model
        4. Parse and return JSON result

    Returns dict with primary_mood, mood_scores, scene_description, reasoning.
    Returns None on failure.
    """
    logger.info(f"  🎞️  Extracting frames: {os.path.basename(video_path)}")
    frames = extract_key_frames(video_path, num_frames=3)

    if not frames:
        logger.warning("  ⚠️  No frames extracted — skipping vision analysis")
        return None

    b64_frames = frames_to_base64(frames)

    # Build multimodal message: images first, then the text prompt
    content = []
    for b64 in b64_frames:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
        })

    prompt_text = PROMPT
    if title:
        prompt_text = f"Video title for context: {title}\n\n{PROMPT}"
    content.append({"type": "text", "text": prompt_text})

    try:
        model  = _get_model()
        client = _get_client()
        logger.info(f"  🤖 Sending {len(frames)} frames → Groq {model}")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}],
            temperature=0.1,
            max_tokens=600,
        )
        raw = response.choices[0].message.content.strip()
        result = _extract_json(raw)

        if result:
            result["raw_response"] = raw
            result["model_used"]   = model
            logger.success(f"  ✅ Mood detected: {result.get('primary_mood')}")
            return result

        logger.warning(f"  ⚠️  JSON parse failed. Raw: {raw[:200]}")
        return None

    except Exception as exc:
        logger.error(f"  ❌ Groq API error: {exc}")
        return None
