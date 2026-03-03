import asyncio
import json
import uuid
from sqlalchemy import select, cast, func, Integer
from database.connection import AsyncSessionLocal
from database.models.interaction import Interaction
from database.models.user import User

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == 'deep'))
        u = result.scalar_one()

        try:
            eng_res = await session.execute(
                select(
                    func.count(Interaction.id).label("total_plays"),
                    func.sum(cast(Interaction.is_liked, Integer)).label("total_likes"),
                    func.sum(cast(Interaction.replayed, Integer)).label("total_replays"),
                )
                .where(Interaction.user_id == u.id)
            )
            eng_stats = eng_res.first()
            print("Query 1 success!", eng_stats)
        except Exception as e:
            print("Query 1 failed:", e)

asyncio.run(main())
