"""
image_analysis.py

This module provides a function to analyze an image using either Ollama or OpenAI LLMs.
It supports local file paths for Ollama and automatically encodes images as base64 data 
URLs for OpenAI.
"""

import base64
import json
import logging
import os
import time
from typing import TypedDict, Union

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from llm_factory import LLMType, get_llm

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()


def image_to_base64_data_url(image_path):
    """
    Convert a local image file to a base64-encoded data URL.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Data URL string suitable for OpenAI API.
    """
    ext = os.path.splitext(image_path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    with open(image_path, "rb") as img_file:
        b64 = base64.b64encode(img_file.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


class ImageAnalysisResult(TypedDict):
    """
    TypedDict for the structured output of analyze_image.
    Fields:
        person_present (bool | None): Whether a person is present in the image.
        description (str): Short description of the person or a message if no person is detected.
    """
    person_present: Union[bool, None]
    description: str


def analyze_image(
    image_path,
    provider="ollama",
    openai_api_key=None,
    model=None,
    temperature=0.1
) -> ImageAnalysisResult:
    """
    Analyze the image using the selected LLM provider (Ollama or OpenAI) and 
    return a structured description.

    Args:
        image_path (str): The path to the image to be analyzed.
        provider (str or LLMType): 'ollama', 'openai', LLMType.OLLAMA, or LLMType.OPENAI.
        openai_api_key (str): Your OpenAI API key if using OpenAI.
        model (str, optional): Model name to use for the LLM provider.
        temperature (float, optional): Sampling temperature for the LLM.

    Returns:
        ImageAnalysisResult: Structured output with keys 'person_present' (bool or None) 
        and 'description' (str).
    """
    if not os.path.exists(image_path) and not (
        image_path.startswith(
            "http://") or image_path.startswith("https://") or image_path.startswith("data:")
    ):
        logging.error("Image file does not exist: %s", image_path)
        return {"person_present": None, "description": f"Image file not found: {image_path}"}

    if provider == "openai" or (isinstance(provider, LLMType) and provider == LLMType.OPENAI):
        if openai_api_key is None:
            openai_api_key = os.getenv("OPENAI_API_KEY")
        # Convert local file to base64 data URL for OpenAI
        if not (image_path.startswith("http://")
                or image_path.startswith("https://")
                or image_path.startswith("data:")):
            image_url = image_to_base64_data_url(image_path)
        else:
            image_url = image_path
    else:
        image_url = image_path

    prompt = get_prompt_from_schema(ImageAnalysisResult)
    try:
        llm = get_llm(provider=provider, openai_api_key=openai_api_key,
                      model=model, temperature=temperature)
        messages = [
            HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ])
        ]
        response = llm.invoke(messages)
        content = response.content.strip() if hasattr(
            response, 'content') else str(response).strip()
        # Handle Markdown code block wrapping (e.g., ```json ... ```
        if content.startswith('```'):
            # Remove code block markers and optional 'json' label
            lines = content.splitlines()
            if lines[0].strip().startswith('```'):
                lines = lines[1:] if lines[0].strip() in (
                    '```', '```json') else lines
            if lines and lines[-1].strip().startswith('```'):
                lines = lines[:-1]
            content = '\n'.join(lines).strip()
        try:
            # If content is already a dict, return it directly
            if isinstance(content, dict):
                structured: ImageAnalysisResult = content
            else:
                structured: ImageAnalysisResult = json.loads(content)
        except json.JSONDecodeError:
            # Try to parse again if the content is a quoted
            # JSON string (double-encoded or with Python literals)
            if isinstance(content, str) and ((content.startswith('{')
                                              and content.endswith('}'))
                                             or (content.startswith('[')
                                                 and content.endswith(']'))):
                try:
                    # Replace Python literals with JSON equivalents
                    safe_content = content.replace("'", '"') \
                        .replace('True', 'true') \
                        .replace('False', 'false') \
                        .replace('None', 'null')
                    structured: ImageAnalysisResult = json.loads(safe_content)
                except json.JSONDecodeError:
                    logging.error(
                        "Failed to parse LLM response as JSON: %s", content)
                    structured = {"person_present": None,
                                  "description": content}
            else:
                logging.error(
                    "Failed to parse LLM response as JSON: %s", content)
                structured = {"person_present": None, "description": content}
        return structured
    except json.JSONDecodeError as e:
        # Handle JSON errors specifically
        logging.exception("LLM call failed (JSONDecodeError)")
        return {"person_present": None, "description": f"LLM error: {e}"}
    except (TypeError, ValueError) as e:
        logging.exception("LLM call failed (TypeError/ValueError)")
        return {"person_present": None, "description": f"LLM error: {e}"}
    except OSError as e:
        # Handle file errors specifically
        logging.exception("LLM call failed (OSError)")
        return {"person_present": None, "description": f"LLM error: {e}"}


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


# Example usage
if __name__ == "__main__":
    IMAGE_PATH = './images/Screenshot-NoPerson.png'  # Replace with your image path
    start_time = time.time()

    # Set default models if not provided
    # For Ollama, ensure the model is pulled: ollama pull llava:latest
    # (or use another installed vision model)
    # Change to your preferred/installed local Ollama model
    OLLAMA_MODEL = "llama3.2-vision:latest"
    # For OpenAI, use the latest available vision model
    # (see https://platform.openai.com/docs/models/gpt-4o)
    OPENAI_MODEL = "gpt-4o-mini"  # Change to your preferred OpenAI model

    # Use Ollama (local)
    # result = analyze_image(
    #     IMAGE_PATH, provider=LLMType.OLLAMA, model=OLLAMA_MODEL, temperature=0)
    # logging.info("Ollama result: %s", result)

    # Use OpenAI (API key loaded from .env if not provided)
    result = analyze_image(
        IMAGE_PATH, provider=LLMType.OPENAI, model=OPENAI_MODEL, temperature=0)
    logging.info("OpenAI result: %s", result)

    end_time = time.time()
    execution_time = end_time - start_time
    logging.info("Script execution time: %.2f seconds", execution_time)
