import asyncio
from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models.mood import VideoMood
import uuid

async def check():
    async with AsyncSessionLocal() as session:
        ids = [
            uuid.UUID("dfb7dd7b-be4c-4e8c-859a-df5fb9bf7a5f"), # placeholder, need to be careful
            uuid.UUID("4ef270a6-16e6-4de3-4965-a2e3-1963da1c1490")
        ]
        # Wait, I'll just check for ANY mood for these IDs
        for vid_id in ids:
            res = await session.execute(select(VideoMood).where(VideoMood.video_id == vid_id))
            mood = res.scalar_one_or_none()
            print(f"Video {vid_id} mood: {mood}")

if __name__ == "__main__":
    asyncio.run(check())
