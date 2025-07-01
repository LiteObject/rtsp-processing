"""
image_analysis.py

Async image analysis using aiohttp for OpenAI API calls.
"""
import asyncio
import base64
import json
import logging
import os
from typing import Any, Dict, TypedDict, Union

import aiohttp
from langchain_core.messages import HumanMessage

from .config import Config
from .llm_factory import get_llm


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


async def analyze_image_async(
    image_path: str,
    provider: str = None,
    model: str = None,
    temperature: float = None,
    openai_api_key: str = None,
) -> Dict[str, Any]:
    """
    Async version of image analysis using LangChain LLM abstraction.

    Args:
        image_path (str): Path to image file
        provider (str): LLM provider (e.g., 'openai', 'ollama')
        model (str): Model name for the LLM provider
        temperature (float): Sampling temperature for the LLM
        openai_api_key (str): OpenAI API key if using OpenAI
    Returns:
        Dict containing person_present and description
    """
    # Input validation
    if not isinstance(image_path, str) or not image_path.strip():
        raise ValueError("Invalid image path provided")

    # Use config default if no provider specified
    if not provider:
        provider = Config.DEFAULT_LLM_PROVIDER

    # Provider validation (for now only OpenAI is supported)
    if provider.lower() != "openai":
        raise ValueError(
            "Only OpenAI provider supported for async image analysis")

    # Check if file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Convert image to base64 data URL
    data_url = image_to_base64_data_url(image_path)

    # Prepare prompt
    prompt = get_prompt_from_schema(ImageAnalysisResult)

    # Get LLM using factory
    llm = get_llm(provider)

    # LangChain expects a list of HumanMessage objects with proper content structure
    lc_messages = [HumanMessage(content=[
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": data_url}}
    ])]

    # Async invoke with retry logic
    for attempt in range(Config.MAX_RETRIES):
        try:
            response = await llm.ainvoke(lc_messages)
            content = response.content.strip() if hasattr(
                response, 'content') else str(response).strip()

            if not content:
                logging.error("Empty response from LLM")
                continue

            # Try to parse as JSON with markdown cleanup
            clean_content = content.strip()
            if clean_content.startswith('```json'):
                clean_content = clean_content[7:]
            if clean_content.endswith('```'):
                clean_content = clean_content[:-3]
            clean_content = clean_content.strip()

            try:
                return json.loads(clean_content)
            except json.JSONDecodeError:
                logging.error("Invalid JSON from %s (attempt %d): %s",
                              provider, attempt + 1, content[:100])
                if attempt < Config.MAX_RETRIES - 1:
                    await asyncio.sleep(Config.RETRY_DELAY * (2 ** attempt))
                    continue
                return {"person_present": None, "description": content[:200]}

        except (json.JSONDecodeError, ValueError, AttributeError, TypeError, RuntimeError, OSError) as e:
            if attempt < Config.MAX_RETRIES - 1:
                logging.warning("LLM call failed (attempt %d/%d): %s",
                                attempt + 1, Config.MAX_RETRIES, e)
                await asyncio.sleep(Config.RETRY_DELAY * (2 ** attempt))
            else:
                logging.error("All LLM attempts failed: %s", e)
                return {"person_present": None, "description": f"Analysis failed: {e}"}

    return {"person_present": None, "description": "Analysis failed after retries"}


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
            processed_results.append(
                {"person_present": None, "description": "Processing failed"})
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
        logging.debug("Processed %s: %s", path, result)


if __name__ == "__main__":
    asyncio.run(demo_async_analysis())
