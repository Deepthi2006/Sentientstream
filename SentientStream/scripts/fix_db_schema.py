import asyncio
from sqlalchemy import text
from database.connection import engine

async def fix_schema():
    async with engine.begin() as conn:
        print("🔍 Checking schema for 'videos' table...")
        
        # Add is_user_upload column
        try:
            await conn.execute(text("ALTER TABLE videos ADD COLUMN is_user_upload INTEGER DEFAULT 0"))
            print("✅ Added column 'is_user_upload'")
        except Exception as e:
            if "already exists" in str(e):
                print("ℹ️ Column 'is_user_upload' already exists.")
            else:
                print(f"❌ Error adding 'is_user_upload': {e}")

        # Make pexels_id nullable
        try:
            await conn.execute(text("ALTER TABLE videos ALTER COLUMN pexels_id DROP NOT NULL"))
            print("✅ Made 'pexels_id' nullable")
        except Exception as e:
            print(f"❌ Error altering 'pexels_id': {e}")

if __name__ == "__main__":
    asyncio.run(fix_schema())
