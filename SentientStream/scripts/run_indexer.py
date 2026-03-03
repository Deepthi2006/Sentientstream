"""
scripts/run_indexer.py
───────────────────────
STEP 3 — Generate embeddings and build the FAISS vector index.

Usage:
    cd d:\aws\SentientStream
    python -m scripts.run_indexer
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loguru import logger
from vector_store.indexer import build_faiss_index


async def main():
    logger.info("=" * 55)
    logger.info("  SentientStream — Step 3: Build FAISS Index")
    logger.info("=" * 55)

    await build_faiss_index()

    logger.success(
        "\n✅ FAISS index ready!\n"
        "Next step: start the API server with:\n"
        "   python -m backend.main"
    )


if __name__ == "__main__":
    asyncio.run(main())
