"""
test_llm_factory.py

Unit tests for the LLM factory in src/llm_factory.py, 
covering provider selection, API key handling, and error cases.
"""

import pytest
from src.llm_factory import get_llm, LLMProvider


def test_get_llm_ollama():
    """
    Test that get_llm returns a valid LLM instance for the Ollama provider.
    """
    llm = get_llm(provider=LLMProvider.OLLAMA,
                  model="llama3.2-vision", temperature=0.1)
    assert llm is not None
    assert hasattr(llm, "invoke")


def test_get_llm_openai(monkeypatch):
    """
    Test that get_llm returns a valid LLM instance for the OpenAI provider when API key is set.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    llm = get_llm(provider=LLMProvider.OPENAI, model="gpt-4o", temperature=0.1)
    assert llm is not None
    assert hasattr(llm, "invoke")


def test_get_llm_invalid_provider():
    """
    Test that get_llm raises ValueError for an invalid provider.
    """
    with pytest.raises(ValueError):
        get_llm(provider="invalid")


def test_get_llm_missing_api_key(monkeypatch):
    """
    Test that get_llm raises ValueError if the OpenAI API key is missing.
    """
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError):
        get_llm(provider=LLMProvider.OPENAI)
