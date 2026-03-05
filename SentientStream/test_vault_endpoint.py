import asyncio
import json
import httpx
from database.connection import AsyncSessionLocal
from database.models.user import User
from backend.auth_utils import create_access_token

async def test_vault_endpoint():
    async with AsyncSessionLocal() as session:
        # Get a user who has interactions
        user_res = await session.execute(select(User).limit(1))
        user = user_res.scalar_one_or_none()
        if not user:
            print("No users found")
            return

        token = create_access_token({"sub": str(user.id)})
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "http://localhost:8000/user/vault",
                headers={"Authorization": f"Bearer {token}"}
            )
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.text}")

if __name__ == "__main__":
    from sqlalchemy import select
    asyncio.run(test_vault_endpoint())
