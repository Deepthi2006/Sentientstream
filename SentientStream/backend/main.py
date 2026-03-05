"""
backend/main.py
────────────────
FastAPI application entry point for SentientStream.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import videos, feed

load_dotenv()
"""
app = FastAPI(
    title="SentientStream API",
backend/main.py
────────────────
FastAPI application entry point for SentientStream.

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import videos, feed

load_dotenv()
"""
app = FastAPI(
    title="SentientStream API",
    description="Mood-based video streaming powered by AI 🎬",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
<<<<<<< HEAD
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173", 
        "http://localhost:3000", 
        "http://localhost:5174",
        "http://18.204.214.91"
    ],
=======
    allow_origins=["http://18.204.214.91"],  # frontend URL
>>>>>>> cc968d96bfa0b5b5c460e20254f7dddf20efbfce
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(videos.router)
app.include_router(feed.router)
from backend.routers import auth, interactions, user
app.include_router(auth.router)
app.include_router(interactions.router)
app.include_router(user.router)

@app.get("/", tags=["health"])
async def root():
    return {
        "service": "SentientStream API",
        "status":  "running",
        "docs":    "/docs",
    }


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    logger.info(f"🚀 Starting SentientStream API on port {port}")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
