import asyncio
from sqlalchemy import select, func, desc
from database.connection import AsyncSessionLocal
from database.models.interaction import Interaction
from database.models.mood import VideoMood
from database.models.user import User

async def test_vault_for_all():
    async with AsyncSessionLocal() as session:
        users_res = await session.execute(select(User))
        for user in users_res.scalars().all():
            print(f"\nUser: {user.username} ({user.id})")
            
            # This is the exact query from the router
            mood_result = await session.execute(
                select(
                    VideoMood.primary_mood,
                    func.count(Interaction.id).label("watch_count")
                )
                .select_from(Interaction)
                .join(VideoMood, VideoMood.video_id == Interaction.video_id)
                .where(Interaction.user_id == user.id)
                .group_by(VideoMood.primary_mood)
                .order_by(desc("watch_count"))
                .limit(3)
            )
            
            rows = mood_result.all()
            print(f"  Rows found: {len(rows)}")
            for row in rows:
                print(f"    Mood: {row.primary_mood} | Count: {row.watch_count}")

if __name__ == "__main__":
    asyncio.run(test_vault_for_all())
