import asyncio
import httpx
from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models.user import User
from backend.auth_utils import create_access_token

async def test_all_vaults():
    async with AsyncSessionLocal() as session:
        users = await session.execute(select(User))
        for user in users.scalars().all():
            token = create_access_token({"sub": str(user.id)})
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "http://localhost:8000/user/vault",
                    headers={"Authorization": f"Bearer {token}"}
                )
                print(f"User: {user.username} | Status: {resp.status_code} | Memories: {len(resp.json().get('memories', []))}")

if __name__ == "__main__":
    asyncio.run(test_all_vaults())
