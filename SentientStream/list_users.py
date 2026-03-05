import asyncio
from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models.user import User

async def check():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User.username))
        print(res.scalars().all())

if __name__ == "__main__":
    asyncio.run(check())
