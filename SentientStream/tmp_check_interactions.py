import asyncio
from sqlalchemy import select, func
from database.connection import AsyncSessionLocal
from database.models.interaction import Interaction

async def check():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count(Interaction.id)))
        print(f"Total Interactions: {result.scalar()}")

if __name__ == "__main__":
    asyncio.run(check())
