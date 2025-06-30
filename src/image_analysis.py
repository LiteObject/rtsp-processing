"""
image_analysis.py

Async image analysis using aiohttp for OpenAI API calls.
"""
import asyncio
import aiohttp
import base64
import json
import logging
import os
from typing import Dict, Any

from .config import Config


async def analyze_image_async(image_path: str, provider: str = "openai") -> Dict[str, Any]:
    """
    Async version of image analysis using OpenAI API.
    
    Args:
        image_path (str): Path to image file
        provider (str): LLM provider (only openai supported in this demo)
        
    Returns:
        Dict containing person_present and description
    """
    if provider != "openai":
        raise ValueError("Only OpenAI supported in async demo")
    
    # Convert image to base64
    with open(image_path, "rb") as img_file:
        b64_data = base64.b64encode(img_file.read()).decode()
    
    data_url = f"data:image/jpeg;base64,{b64_data}"
    
    # Prepare API request
    headers = {
        "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": Config.DEFAULT_LLM_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "Respond ONLY with JSON: {\"person_present\": true/false, \"description\": \"brief description\"}"},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]
        }],
        "temperature": Config.LLM_TEMPERATURE,
        "max_tokens": 100
    }
    
    # Async HTTP request with retry
    for attempt in range(Config.MAX_RETRIES):
        try:
            timeout = aiohttp.ClientTimeout(total=Config.LLM_TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        return json.loads(content.strip())
                    else:
                        raise aiohttp.ClientError(f"API error: {response.status}")
                        
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt < Config.MAX_RETRIES - 1:
                logging.warning("Async LLM call failed (attempt %d/%d): %s", attempt + 1, Config.MAX_RETRIES, e)
                await asyncio.sleep(Config.RETRY_DELAY * (2 ** attempt))
            else:
                raise
    
    return {"person_present": None, "description": "Analysis failed"}


async def process_multiple_images_async(image_paths: list[str]) -> list[Dict[str, Any]]:
    """
    Process multiple images concurrently using async.
    
    Args:
        image_paths: List of image file paths
        
    Returns:
        List of analysis results
    """
    tasks = [analyze_image_async(path) for path in image_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logging.error("Failed to process %s: %s", image_paths[i], result)
            processed_results.append({"person_present": None, "description": "Processing failed"})
        else:
            processed_results.append(result)
    
    return processed_results


# Demo usage
async def demo_async_analysis():
    """Demonstrate async image analysis."""
    image_paths = ["images/test1.jpg", "images/test2.jpg", "images/test3.jpg"]
    
    # Process all images concurrently
    results = await process_multiple_images_async(image_paths)
    
    for path, result in zip(image_paths, results):
        print(f"{path}: {result}")


if __name__ == "__main__":
    asyncio.run(demo_async_analysis())