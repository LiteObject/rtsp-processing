"""
Module for testing image processing functions.

This module contains unit tests for functions in the image_analysis module,
specifically testing image-to-base64 conversion, prompt generation from schema,
and image analysis results processing.
"""
import pytest
from src.image_analysis import image_to_base64_data_url, get_prompt_from_schema, ImageAnalysisResult


def test_image_to_base64_data_url_png(tmp_path):
    """
    Test the image_to_base64_data_url function.

    This test creates a temporary PNG image file, converts it to a 
    base64 data URL using the image_to_base64_data_url function, 
    and asserts that the resulting URL starts with the correct prefix.

    Args:
        tmp_path: A pytest fixture that provides a temporary directory unique to the test invocation.
    """
    img_path = tmp_path / "test.png"
    img_path.write_bytes(b"\x89PNG\r\n\x1a\n")
    url = image_to_base64_data_url(str(img_path))
    assert url.startswith("data:image/png;base64,")


def test_image_to_base64_data_url_jpg(tmp_path):
    """
    Test the image_to_base64_data_url function with a JPEG image.

    This test creates a temporary JPEG image file, converts it to a 
    base64 data URL using the image_to_base64_data_url function, 
    and asserts that the resulting URL starts with the correct prefix.

    Args:
        tmp_path: A pytest fixture that provides a temporary directory unique to the test invocation.
    """
    img_path = tmp_path / "test.jpg"
    img_path.write_bytes(b"\xff\xd8\xff")
    url = image_to_base64_data_url(str(img_path))
    assert url.startswith("data:image/jpeg;base64,")


def test_image_to_base64_data_url_missing():
    """
    Test the image_to_base64_data_url function for a missing file.

    This test verifies that a FileNotFoundError is raised when attempting 
    to convert a non-existent image file to a base64 data URL.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    with pytest.raises(FileNotFoundError):
        image_to_base64_data_url("not_a_file.png")


def test_get_prompt_from_schema():
    """
    Test the get_prompt_from_schema function.

    This test checks that the prompt generated from the ImageAnalysisResult schema 
    contains the expected key "person_present". It verifies that the function correctly 
    extracts relevant information from the schema.

    Asserts:
        - "person_present" should be present in the generated prompt.
        - "description" should also be present in the prompt.
    """
    prompt = get_prompt_from_schema(ImageAnalysisResult)
    assert "person_present" in prompt
    assert "description" in prompt
    assert prompt.startswith("Respond ONLY with a JSON object")
