import asyncio
import os
from dotenv import load_dotenv
from backend.ai_utils import generate_sentient_text

load_dotenv()

async def test_fallback():
    print("Testing AI Fallback (Bedrock -> Groq)...")
    res = await generate_sentient_text("Tell me a sentient movie line about vectors.")
    print(f"Result: {res}")

if __name__ == "__main__":
    asyncio.run(test_fallback())
