from __future__ import annotations

from typing import Dict

from .base import GenAIProvider, GenAIProviderName
from .bedrock_provider import BedrockProvider
from .google_provider import GoogleGenAIProvider


_PROVIDER_SINGLETONS: Dict[GenAIProviderName, GenAIProvider] = {
    "google": GoogleGenAIProvider(),
    "amazon": BedrockProvider(),
}


def get_provider(name: GenAIProviderName) -> GenAIProvider:
    try:
        return _PROVIDER_SINGLETONS[name]
    except KeyError as e:
        raise ValueError(f"Unsupported GenAI provider: {name}") from e
