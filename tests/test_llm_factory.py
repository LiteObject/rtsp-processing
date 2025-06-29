import pytest
from src.llm_factory import get_llm, LLMProvider


def test_get_llm_ollama():
    llm = get_llm(provider=LLMProvider.OLLAMA,
                  model="llama3.2-vision", temperature=0.1)
    assert llm is not None
    assert hasattr(llm, "invoke")


def test_get_llm_openai(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    llm = get_llm(provider=LLMProvider.OPENAI, model="gpt-4o", temperature=0.1)
    assert llm is not None
    assert hasattr(llm, "invoke")


def test_get_llm_invalid_provider():
    with pytest.raises(ValueError):
        get_llm(provider="invalid")


def test_get_llm_missing_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError):
        get_llm(provider=LLMProvider.OPENAI)
