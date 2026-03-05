import asyncio
from sqlalchemy import select, func
from database.connection import AsyncSessionLocal
from database.models.interaction import Interaction
from database.models.mood import VideoMood
from database.models.user import User

async def debug_vault():
    async with AsyncSessionLocal() as session:
        # Get all users
        users_res = await session.execute(select(User.id, User.username))
        users = users_res.all()
        print(f"Users in DB: {users}")

        for user_id, username in users:
            print(f"\nChecking data for user: {username} ({user_id})")
            
            # Total interactions for this user
            int_res = await session.execute(
                select(func.count(Interaction.id)).where(Interaction.user_id == user_id)
            )
            print(f"  Total Interactions: {int_res.scalar()}")

            # Check if interactions join with moods
            join_res = await session.execute(
                select(func.count(Interaction.id))
                .join(VideoMood, VideoMood.video_id == Interaction.video_id)
                .where(Interaction.user_id == user_id)
            )
            print(f"  Interactions with Moods: {join_res.scalar()}")

            # Sample interactions
            sample_res = await session.execute(
                select(Interaction.video_id, Interaction.user_id).limit(5)
            )
            print(f"  Sample Interactions (video_id | user_id):")
            for row in sample_res:
                print(f"    {row[0]} | {row[1]}")

if __name__ == "__main__":
    asyncio.run(debug_vault())
