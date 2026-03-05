import asyncio
from sqlalchemy import select, func
from database.connection import AsyncSessionLocal
from database.models.video import Video
from database.models.mood import VideoMood

async def check():
    async with AsyncSessionLocal() as session:
        v = await session.execute(select(func.count(Video.id)))
        m = await session.execute(select(func.count(VideoMood.id)))
        print(f"Videos: {v.scalar()}")
        print(f"Moods: {m.scalar()}")

if __name__ == "__main__":
    asyncio.run(check())
