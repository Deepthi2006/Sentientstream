import asyncio
from sqlalchemy import select, func
from database.connection import AsyncSessionLocal
from database.models.interaction import Interaction
from database.models.mood import VideoMood
from database.models.user import User

async def debug_vault_minimal():
    async with AsyncSessionLocal() as session:
        # Check current user interactions
        # I'll just check for ALL interactions first to see if they join ANYWHERE
        res = await session.execute(
            select(
                Interaction.user_id,
                func.count(Interaction.id).label("total"),
                func.count(VideoMood.id).label("with_mood")
            )
            .outerjoin(VideoMood, VideoMood.video_id == Interaction.video_id)
            .group_by(Interaction.user_id)
        )
        print("User Stats:")
        for row in res:
            print(f"User: {row[0]} | Total: {row[1]} | With Mood: {row[2]}")

if __name__ == "__main__":
    asyncio.run(debug_vault_minimal())
