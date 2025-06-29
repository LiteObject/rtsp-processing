import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import os
from src.image_analysis import analyze_image, ImageAnalysisResult


class TestAnalyzeImage:
    
    @patch('src.image_analysis.image_to_base64_data_url')
    @patch('src.image_analysis.get_llm')
    @patch('src.image_analysis.os.path.exists')
    def test_analyze_image_person_detected_openai(self, mock_exists, mock_get_llm, mock_base64):
        # Setup
        mock_exists.return_value = True
        mock_base64.return_value = "data:image/jpeg;base64,test"
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = '{"person_present": true, "description": "Person walking"}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        # Execute
        result = analyze_image("test.jpg", provider="openai")
        
        # Assert
        assert result["person_present"] is True
        assert result["description"] == "Person walking"
        mock_get_llm.assert_called_once()

    @patch('src.image_analysis.get_llm')
    @patch('src.image_analysis.os.path.exists')
    def test_analyze_image_no_person_detected(self, mock_exists, mock_get_llm):
        # Setup
        mock_exists.return_value = True
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = '{"person_present": false, "description": "Empty room"}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        # Execute
        result = analyze_image("test.jpg", provider="ollama")
        
        # Assert
        assert result["person_present"] is False
        assert result["description"] == "Empty room"

    @patch('src.image_analysis.get_llm')
    @patch('src.image_analysis.os.path.exists')
    def test_analyze_image_json_with_code_blocks(self, mock_exists, mock_get_llm):
        # Setup
        mock_exists.return_value = True
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = '```json\n{"person_present": true, "description": "Person detected"}\n```'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        # Execute
        result = analyze_image("test.jpg")
        
        # Assert
        assert result["person_present"] is True
        assert result["description"] == "Person detected"

    @patch('src.image_analysis.get_llm')
    @patch('src.image_analysis.os.path.exists')
    def test_analyze_image_invalid_json_response(self, mock_exists, mock_get_llm):
        # Setup
        mock_exists.return_value = True
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = 'Invalid JSON response'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        # Execute
        result = analyze_image("test.jpg")
        
        # Assert
        assert result["person_present"] is None
        assert "Invalid JSON response" in result["description"]

    @patch('src.image_analysis.os.path.exists')
    def test_analyze_image_file_not_found(self, mock_exists):
        # Setup
        mock_exists.return_value = False
        
        # Execute
        result = analyze_image("nonexistent.jpg")
        
        # Assert
        assert result["person_present"] is None
        assert "Image file not found" in result["description"]

    @patch('src.image_analysis.get_llm')
    @patch('src.image_analysis.os.path.exists')
    def test_analyze_image_llm_exception(self, mock_exists, mock_get_llm):
        # Setup
        mock_exists.return_value = True
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("LLM error")
        mock_get_llm.return_value = mock_llm
        
        # Execute
        try:
            result = analyze_image("test.jpg")
            # If no exception is raised, check the result
            assert result["person_present"] is None
            assert "LLM error" in result["description"]
        except Exception as e:
            # If exception is raised, that's also acceptable
            assert "LLM error" in str(e)

    @patch('src.image_analysis.image_to_base64_data_url')
    @patch('src.image_analysis.get_llm')
    @patch('src.image_analysis.os.path.exists')
    def test_analyze_image_openai_base64_conversion(self, mock_exists, mock_get_llm, mock_base64):
        # Setup
        mock_exists.return_value = True
        mock_base64.return_value = "data:image/jpeg;base64,test"
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = '{"person_present": true, "description": "Test"}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        # Execute
        analyze_image("test.jpg", provider="openai")
        
        # Assert
        mock_base64.assert_called_once_with("test.jpg")