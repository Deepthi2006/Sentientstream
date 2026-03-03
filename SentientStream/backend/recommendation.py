import numpy as np
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.interaction import Interaction
from database.models.user import User
from database.models.embedding import VideoEmbedding
from vector_store.faiss_store import FAISSStore
from loguru import logger
from sqlalchemy.orm import selectinload

def get_faiss_store() -> FAISSStore:
    from backend.routers.feed import get_store
    return get_store()

async def update_user_embedding(user_id: str, db: AsyncSession):
    # Fetch all user interactions and load associated videos to get duration
    result = await db.execute(
        select(Interaction)
        .options(selectinload(Interaction.video))
        .where(Interaction.user_id == user_id)
    )
    interactions = result.scalars().all()

    if not interactions:
        return

    # Fetch video FAISS index positions mapping
    video_ids = [str(i.video_id) for i in interactions]
    result_vecs = await db.execute(
        select(VideoEmbedding).where(VideoEmbedding.video_id.in_(video_ids))
    )
    faiss_map = {str(ve.video_id): ve.faiss_index_id for ve in result_vecs.scalars().all()}

    store = get_faiss_store()
    
    user_vector = np.zeros(store.dim, dtype=np.float32)
    total_weight = 0.0

    for inter in interactions:
        vid_str = str(inter.video_id)
        if vid_str not in faiss_map:
            continue
        
        faiss_id = faiss_map[vid_str]
        try:
            vec = store.index.reconstruct(faiss_id)
        except Exception as e:
            logger.warning(f"Could not reconstruct faiss_id {faiss_id}: {e}")
            continue

        vid_duration = inter.video.duration if (inter.video and inter.video.duration > 0) else 15.0
        watch_percentage = inter.watch_duration / float(vid_duration)

        weight = 0.0

        # Short watch time reduces weight (negative weight pushes vector away from this content)
        if watch_percentage < 0.25:
            weight -= 2.0
        else:
            # Higher watch time increases weight appropriately
            weight += min(watch_percentage * 3.0, 6.0)

        # Completed status
        if watch_percentage >= 0.95:
            weight += 2.0

        # Liked
        if inter.is_liked:
            weight += 5.0
            
        # Replayed
        if inter.replayed:
            weight += 3.0
            
        # Paused count
        if inter.paused_count > 0:
            weight += min(inter.paused_count * 1.0, 3.0)
        
        user_vector += weight * vec
        total_weight += abs(weight)

    if total_weight > 0:
        user_vector = user_vector / np.linalg.norm(user_vector)  # normalize
        # save to user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.user_embedding = user_vector.tolist()
            await db.commit()
            logger.info(f"Embedding Evolution | User: {user_id} | Total weight computed: {total_weight:.2f} | Vector snapshot: {user.user_embedding[:5]}...")
