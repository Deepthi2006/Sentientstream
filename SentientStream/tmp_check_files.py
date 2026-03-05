import asyncio
from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models.video import Video
import os

async def check():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Video).limit(5))
        for v in result.scalars().all():
            exists = os.path.exists(v.local_path) if v.local_path else False
            print(f"ID: {v.id} | Status: {v.status} | Path: {v.local_path} | Exists: {exists}")

if __name__ == "__main__":
    asyncio.run(check())
