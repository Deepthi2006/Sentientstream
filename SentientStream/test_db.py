import asyncio
from sqlalchemy import select, func
from database.connection import AsyncSessionLocal
from database.models.interaction import Interaction
from database.models.user import User

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count(Interaction.id)))
        print(f"Total interactions: {result.scalar()}")

        result2 = await session.execute(select(User))
        users = result2.scalars().all()
        for u in users:
            print(f"User: {u.username} ID: {u.id}")

asyncio.run(main())
