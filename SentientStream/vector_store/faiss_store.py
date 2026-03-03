"""
vector_store/faiss_store.py
────────────────────────────
FAISS flat inner-product index for video embedding search.
For normalised vectors, inner product == cosine similarity.

Persists to disk as:
    vector_store/data/faiss.index
    vector_store/data/faiss_metadata.json
"""
import os
import json
import numpy as np
import faiss
from pathlib import Path
from loguru import logger
from typing import Optional

DATA_DIR         = "vector_store/data"
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss.index")
FAISS_META_PATH  = os.path.join(DATA_DIR, "faiss_metadata.json")
EMBEDDING_DIM    = 384

Path(DATA_DIR).mkdir(parents=True, exist_ok=True)


class FAISSStore:
    """
    Wraps a FAISS IndexFlatIP (cosine similarity for L2-normalised vectors).

    Metadata list mirrors the index row-by-row:
        [{"faiss_id": 0, "video_id": "uuid", "mood": "calm"}, ...]
    """

    def __init__(self, dim: int = EMBEDDING_DIM) -> None:
        self.dim      = dim
        self.index    = faiss.IndexFlatIP(dim)
        self.metadata: list[dict] = []

    # ── write ──────────────────────────────────────────────────────────────

    def add(self, embedding: np.ndarray, video_id: str, mood: str) -> int:
        """Add one vector. Returns its FAISS index position (faiss_id)."""
        faiss_id = self.index.ntotal
        self.index.add(embedding.reshape(1, -1).astype("float32"))
        self.metadata.append({"faiss_id": faiss_id,
                               "video_id": video_id,
                               "mood":     mood})
        return faiss_id

    # ── read ───────────────────────────────────────────────────────────────

    def search(self,
               query: np.ndarray,
               k: int = 10,
               mood_filter: Optional[str] = None,
               excluded_video_ids: Optional[set[str]] = None) -> list[dict]:
        """
        Return top-k similar videos.
        If mood_filter is set, only returns records whose mood matches.
        If excluded_video_ids is set, ensures these videos are not returned.
        Searches a larger candidate pool before filtering to ensure enough results.
        """
        if self.index.ntotal == 0:
            logger.warning("FAISS index is empty")
            return []

        # Find more candidates if we have filters, user could have watched many videos
        search_k = min(k * 20 if (mood_filter or excluded_video_ids) else k, self.index.ntotal)
        scores, indices = self.index.search(
            query.reshape(1, -1).astype("float32"), search_k
        )

        results: list[dict] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            meta = dict(self.metadata[idx])
            meta["score"] = float(score)
            
            if mood_filter and meta.get("mood") != mood_filter:
                continue
            if excluded_video_ids and meta["video_id"] in excluded_video_ids:
                continue
                
            results.append(meta)
            if len(results) >= k:
                break

        return results

    # ── persistence ────────────────────────────────────────────────────────

    def save(self) -> None:
        faiss.write_index(self.index, FAISS_INDEX_PATH)
        with open(FAISS_META_PATH, "w") as f:
            json.dump(self.metadata, f, indent=2)
        logger.success(f"💾 FAISS saved — {self.index.ntotal} vectors")

    @classmethod
    def load(cls) -> "FAISSStore":
        store = cls()
        if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(FAISS_META_PATH):
            store.index    = faiss.read_index(FAISS_INDEX_PATH)
            with open(FAISS_META_PATH) as f:
                store.metadata = json.load(f)
            logger.success(f"✅ FAISS loaded — {store.index.ntotal} vectors")
        else:
            logger.warning("No existing FAISS index found — starting fresh")
        return store
