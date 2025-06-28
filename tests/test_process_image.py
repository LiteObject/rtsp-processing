from src.llm_factory import get_llm, LLMType
from src.image_analysis import image_to_base64_data_url, get_prompt_from_schema, ImageAnalysisResult
import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))


def test_image_to_base64_data_url_png(tmp_path):
    # Create a dummy PNG file
    img_path = tmp_path / "test.png"
    img_path.write_bytes(b"\x89PNG\r\n\x1a\n")
    url = image_to_base64_data_url(str(img_path))
    assert url.startswith("data:image/png;base64,")


def test_image_to_base64_data_url_jpg(tmp_path):
    img_path = tmp_path / "test.jpg"
    img_path.write_bytes(b"\xff\xd8\xff")
    url = image_to_base64_data_url(str(img_path))
    assert url.startswith("data:image/jpeg;base64,")


def test_image_to_base64_data_url_missing():
    with pytest.raises(FileNotFoundError):
        image_to_base64_data_url("not_a_file.png")


def test_get_prompt_from_schema():
    prompt = get_prompt_from_schema(ImageAnalysisResult)
    assert "person_present" in prompt
    assert "description" in prompt
    assert prompt.startswith("Respond ONLY with a JSON object")
