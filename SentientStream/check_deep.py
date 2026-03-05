import asyncio
from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models.interaction import Interaction
from database.models.user import User

async def check():
    async with AsyncSessionLocal() as session:
        user_res = await session.execute(select(User).where(User.username == "deep"))
        user = user_res.scalar_one_or_none()
        if not user:
            print("User deep not found")
            return
        
        int_res = await session.execute(select(Interaction).where(Interaction.user_id == user.id))
        for i in int_res.scalars().all():
            print(f"Interaction: video_id={i.video_id}")

if __name__ == "__main__":
    asyncio.run(check())
