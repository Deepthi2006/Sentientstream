import os
import json
import boto3
import aiohttp
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

async def generate_sentient_text(prompt: str, max_tokens: int = 100) -> str:
    """
    Generates cinematic/sentient text using AWS Bedrock (Claude) 
    with a Groq (Llama-3) fallback.
    """
    
    # --- Try AWS Bedrock ---
    if os.getenv("AWS_ACCESS_KEY_ID"):
        try:
            client = boto3.client(
                service_name='bedrock-runtime',
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
            )
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": 0.8,
                "messages": [{"role": "user", "content": prompt}]
            })
            
            response = client.invoke_model(
                modelId="anthropic.claude-3-haiku-20240307-v1:0",
                contentType="application/json",
                accept="application/json",
                body=body
            )
            
            response_body = json.loads(response.get("body").read())
            txt = response_body.get("content")[0].get("text").strip().replace('"', '')
            logger.info("✅ Text generated via Bedrock")
            return txt
        except Exception as e:
            logger.warning(f"⚠️ Bedrock failed: {e}. Falling back to Groq...")

    # --- Try Groq (Llama-3) ---
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": 0.8
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        txt = data['choices'][0]['message']['content'].strip().replace('"', '')
                        logger.info("✅ Text generated via Groq")
                        return txt
                    else:
                        logger.error(f"❌ Groq API error: {resp.status}")
        except Exception as e:
            logger.error(f"❌ Groq fallback failed: {e}")

    # --- Static Fallback ---
    logger.warning("🚫 All AI providers failed. Using static fallback.")
    return "Neural matrix reconstruction complete. The frequency remains undefined."
