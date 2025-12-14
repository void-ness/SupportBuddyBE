from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional


GenAIProviderName = Literal["google", "amazon"]


@dataclass(frozen=True)
class GenerationParams:
    """Provider-agnostic generation parameters.

    Not all providers support all fields; providers should ignore what they can't use.
    """

    temperature: float = 1.5
    max_output_tokens: int = 3000


class GenAIProvider(abc.ABC):
    """Template base class for LLM providers.

    Concrete providers implement the hook methods that build a request
    and parse the response. The `generate_text`/`generate_json` methods
    contain the shared algorithm.
    """

    @abc.abstractmethod
    async def _generate_text_impl(
        self,
        *,
        prompt: str,
        system_prompt: Optional[str],
        model_name: Optional[str],
        params: GenerationParams,
    ) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def _generate_json_impl(
        self,
        *,
        prompt: str,
        system_prompt: Optional[str],
        model_name: Optional[str],
        schema: Optional[Dict[str, Any]],
        params: GenerationParams,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    async def generate_text(
        self,
        *,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_name: Optional[str] = None,
        params: Optional[GenerationParams] = None,
    ) -> str:
        params = params or GenerationParams()
        return await self._generate_text_impl(
            prompt=prompt,
            system_prompt=system_prompt,
            model_name=model_name,
            params=params,
        )

    async def generate_json(
        self,
        *,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_name: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        params: Optional[GenerationParams] = None,
    ) -> Dict[str, Any]:
        params = params or GenerationParams()
        return await self._generate_json_impl(
            prompt=prompt,
            system_prompt=system_prompt,
            model_name=model_name,
            schema=schema,
            params=params,
        )
