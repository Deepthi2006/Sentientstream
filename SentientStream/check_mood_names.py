import asyncio
from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models.mood import VideoMood

async def check():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(VideoMood.primary_mood).limit(10))
        print(res.scalars().all())

if __name__ == "__main__":
    asyncio.run(check())
