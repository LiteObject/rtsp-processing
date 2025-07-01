"""
llm_factory.py

This module provides a factory function to instantiate language model (LLM) objects 
for image processing tasks. Supported providers include Ollama (local) and OpenAI (API).
"""

import os
from enum import Enum

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

load_dotenv()


class LLMProvider(Enum):
    """
    Enum for supported LLM providers.
    """
    OLLAMA = "ollama"
    OPENAI = "openai"


def get_llm(provider: str = "ollama", openai_api_key: str | None = None, **kwargs) -> ChatOllama | ChatOpenAI:
    """
    Factory method to return a LangChain LLM object for image processing.

    Args:
        provider (str or LLMProvider): 'ollama', 'openai', LLMProvider.OLLAMA, or LLMProvider.OPENAI.
        openai_api_key (str): Your OpenAI API key if using OpenAI.
        kwargs: Additional model parameters (e.g., model name, temperature).

    Returns:
        LangChain LLM object (ChatOllama or ChatOpenAI)

    Raises:
        ValueError: If an unsupported provider is specified or OpenAI API key is missing.
    """
    # Input validation
    if not isinstance(provider, (str, LLMProvider)):
        raise ValueError("Provider must be string or LLMProvider enum")

    # Accept both string and LLMProvider enum for provider
    if isinstance(provider, LLMProvider):
        provider = provider.value
    provider = str(provider).lower()

    if provider == "ollama":
        model = kwargs.get("model", "llama3.2-vision")
        temperature = kwargs.get("temperature", 0.1)
        return ChatOllama(model=model, temperature=temperature)
    elif provider == "openai":
        if openai_api_key is None:
            openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "OpenAI API key must be provided for OpenAI provider.")
        model = kwargs.get("model", "gpt-4o")  # Updated default model name
        temperature = kwargs.get("temperature", 0.1)
        return ChatOpenAI(model=model, openai_api_key=openai_api_key, temperature=temperature)
    else:
        raise ValueError("Unsupported provider. Use 'ollama' or 'openai'.")
