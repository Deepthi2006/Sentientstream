"""
ai/frame_extractor.py
─────────────────────
Extracts evenly-spaced key frames from an MP4 file using OpenCV.
Frames are returned as BGR numpy arrays (ready to base64-encode for Groq).
"""
import base64
import cv2
import numpy as np
from pathlib import Path
from loguru import logger
from typing import Optional


def extract_key_frames(video_path: str, num_frames: int = 3) -> list[np.ndarray]:
    """
    Extract `num_frames` evenly-spaced frames from the video.
    Skips the first/last 5% to avoid black title/end cards.

    Returns list of BGR numpy arrays, resized to max 512px wide.
    """
    if not Path(video_path).exists():
        logger.error(f"File not found: {video_path}")
        return []

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open: {video_path}")
        return []

    try:
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total <= 0:
            logger.warning(f"No frames in {video_path}")
            return []

        margin = max(1, int(total * 0.05))
        usable = total - 2 * margin

        if usable <= 0 or num_frames <= 0:
            positions = [total // 2]
        else:
            step = max(1, usable // (num_frames + 1))
            positions = [margin + step * i for i in range(1, num_frames + 1)]

        frames: list[np.ndarray] = []
        for pos in positions:
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
            ret, frame = cap.read()
            if ret and frame is not None:
                # Resize: cap width at 512px to reduce Groq payload size
                h, w = frame.shape[:2]
                if w > 512:
                    scale = 512 / w
                    frame = cv2.resize(frame, (512, int(h * scale)))
                frames.append(frame)

        return frames
    finally:
        cap.release()


def frames_to_base64(frames: list[np.ndarray]) -> list[str]:
    """Encode BGR frames as base64-encoded JPEG strings."""
    result: list[str] = []
    for frame in frames:
        _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        result.append(base64.b64encode(buf).decode("utf-8"))
    return result
