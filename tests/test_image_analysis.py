"""
test_image_analysis.py

Unit tests for the image analysis logic in src/image_analysis.py, 
covering various LLM and file scenarios.
"""
import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.image_analysis import analyze_image_async


class TestAnalyzeImageAsync:
    """
    Test suite for the analyze_image_async function, covering async LLM 
    responses, file existence, and error handling.
    """

    @patch('src.image_analysis.aiohttp.ClientSession')
    @patch('src.image_analysis.aiohttp.ClientSession')
    @patch('builtins.open', create=True)
    def test_analyze_image_async_person_detected_openai(self, mock_open, mock_session):
        """
        Test that analyze_image_async returns correct result when a person is detected.
        """
        # Setup
        mock_file = Mock()
        mock_file.read.return_value = b"fake_image_data"
        mock_open.return_value.__enter__.return_value = mock_file
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [{"message": {"content": '{"person_present": true, "description": "Person walking"}'}}]
        })
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response

        # Execute
        result = asyncio.run(analyze_image_async("test.jpg", provider="openai"))

        # Assert
        assert result["person_present"] is True
        assert result["description"] == "Person walking"

    def test_analyze_image_async_ollama_not_supported(self):
        """
        Test that analyze_image_async raises error for unsupported provider.
        """
        # Execute & Assert
        with pytest.raises(ValueError, match="Only OpenAI supported"):
            asyncio.run(analyze_image_async("test.jpg", provider="ollama"))

    @patch('src.image_analysis.aiohttp.ClientSession')
    @patch('src.image_analysis.os.path.exists')
    def test_analyze_image_async_api_error(self, mock_exists, mock_session):
        """
        Test that analyze_image_async handles API errors correctly.
        """
        # Setup
        mock_exists.return_value = True
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response

        # Execute & Assert
        with pytest.raises(Exception):
            asyncio.run(analyze_image_async("test.jpg", provider="openai"))

    def test_analyze_image_async_file_not_found(self):
        """
        Test that analyze_image_async handles missing files.
        """
        # Execute & Assert
        with pytest.raises(FileNotFoundError):
            asyncio.run(analyze_image_async("nonexistent.jpg"))
