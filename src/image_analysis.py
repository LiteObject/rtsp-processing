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
from typing import TypedDict, Union


class ImageAnalysisResult(TypedDict):
    """
    TypedDict for the structured output of analyze_image.
    Fields:
        person_present (bool | None): Whether a person is present in the image.
        description (str): Short description of the person or a message if no person is detected.
    """
    person_present: Union[bool, None]
    description: str


def image_to_base64_data_url(image_path: str) -> str:
    """
    Convert a local image file to a base64-encoded data URL.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Data URL string suitable for OpenAI API.
    """
    # File size validation
    if os.path.getsize(image_path) > Config.MAX_IMAGE_SIZE:
        raise ValueError("Image file too large")
    
    ext = os.path.splitext(image_path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    with open(image_path, "rb") as img_file:
        data = img_file.read()
        b64 = base64.b64encode(data).decode("utf-8")
        # Clear data from memory
        del data
    return f"data:{mime};base64,{b64}"


def get_prompt_from_schema(schema: type) -> str:
    """
    Generate a prompt string for the LLM based on the schema (TypedDict) docstring and fields.
    Args:
        schema (type): The TypedDict class.
    Returns:
        str: Prompt string for the LLM.
    """
    fields = schema.__annotations__
    example = {k: "..." for k in fields}
    example_json = json.dumps(example)
    doc = schema.__doc__ or ""
    return (
        f"Respond ONLY with a JSON object matching this structure: {example_json}. "
        f"Fields: {doc.strip()}"
    )


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