import asyncio
from sqlalchemy import select, func
from database.connection import AsyncSessionLocal
from database.models.interaction import Interaction
from database.models.user import User

async def check():
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(User.username, func.count(Interaction.id))
            .outerjoin(Interaction, Interaction.user_id == User.id)
            .group_by(User.username)
        )
        for row in res:
            print(f"User: {row[0]} | Interactions: {row[1]}")

if __name__ == "__main__":
    asyncio.run(check())
