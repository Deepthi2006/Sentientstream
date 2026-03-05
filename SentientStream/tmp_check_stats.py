import asyncio
from sqlalchemy import select, func
from database.connection import AsyncSessionLocal
from database.models.video import Video
from database.models.mood import VideoMood
from database.models.embedding import VideoEmbedding

async def check():
    async with AsyncSessionLocal() as session:
        v_total = await session.execute(select(func.count(Video.id)))
        v_ready = await session.execute(select(func.count(Video.id)).where(Video.status == 'ready'))
        m_total = await session.execute(select(func.count(VideoMood.id)))
        e_total = await session.execute(select(func.count(VideoEmbedding.id)))
        
        print(f"Videos Total: {v_total.scalar()}")
        print(f"Videos Ready: {v_ready.scalar()}")
        print(f"Moods Total: {m_total.scalar()}")
        print(f"Embeddings Total: {e_total.scalar()}")

if __name__ == "__main__":
    asyncio.run(check())
