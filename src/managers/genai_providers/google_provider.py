from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

from google import genai
from google.genai.types import (
    Content,
    GenerateContentConfig,
    HttpOptions,
    HttpRetryOptions,
    Part,
    ThinkingConfig,
)

from .base import GenAIProvider, GenerationParams

logger = logging.getLogger(__name__)


class GoogleGenAIProvider(GenAIProvider):
    """Google Gemini provider using `google-genai` async client."""

    _client = None

    @classmethod
    def _get_client(cls):
        if cls._client is None:
            api_key = os.getenv("GOOGLE_GENAI_API_KEY")

            retry_options = HttpRetryOptions(
                attempts=3,
                initial_delay=1.0,
                max_delay=10.0,
                exp_base=2.0,
                jitter=0.1,
            )

            http_options = HttpOptions(
                timeout=60 * 1000,
                retry_options=retry_options,
                api_version="v1",
            )

            sync_client = genai.Client(api_key=api_key, http_options=http_options)
            cls._client = sync_client.aio
        return cls._client

    async def _generate_text_impl(
        self,
        *,
        prompt: str,
        system_prompt: Optional[str],
        model_name: Optional[str],
        params: GenerationParams,
    ) -> str:
        model_name = model_name or os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.5-flash")
        client = self._get_client()

        config_params: Dict[str, Any] = {
            "temperature": params.temperature,
            "max_output_tokens": params.max_output_tokens,
            "thinking_config": ThinkingConfig(thinking_budget=3000),
        }

        if system_prompt:
            config_params["system_instruction"] = [Part.from_text(text=system_prompt)]

        config = GenerateContentConfig(**config_params)

        response = await client.models.generate_content(
            model=model_name,
            contents=[Content(role="user", parts=[Part.from_text(text=prompt)])],
            config=config,
        )

        try:
            if (
                hasattr(response, "candidates")
                and response.candidates
                and len(response.candidates) > 0
                and hasattr(response.candidates[0], "finish_reason")
            ):
                logger.info(
                    "Generated response finish reason: %s",
                    response.candidates[0].finish_reason,
                )

            if hasattr(response, "usage_metadata") and response.usage_metadata:
                usage_meta = response.usage_metadata
                logger.info("Usage Metadata: %s", usage_meta.model_dump(exclude_none=True))
        except Exception as e:
            logger.warning("Error logging response metadata: %s", str(e))

        return response.text

    async def _generate_json_impl(
        self,
        *,
        prompt: str,
        system_prompt: Optional[str],
        model_name: Optional[str],
        schema: Optional[Dict[str, Any]],
        params: GenerationParams,
    ) -> Dict[str, Any]:
        # Existing code path: use gemini response_schema for {message, subject}
        model_name = model_name or os.getenv("GOOGLE_GENAI_MODEL_REMINDER", "gemini-flash-latest")
        client = self._get_client()

        config_params: Dict[str, Any] = {
            "temperature": params.temperature,
            "max_output_tokens": params.max_output_tokens,
            "thinking_config": ThinkingConfig(thinking_budget=3000),
            "response_mime_type": "application/json",
        }

        if system_prompt:
            config_params["system_instruction"] = [Part.from_text(text=system_prompt)]

        # Allow custom schema override, but default to existing one
        if schema is None:
            schema = {
                "type": "object",
                "required": ["message", "subject"],
                "properties": {
                    "message": {"type": "string"},
                    "subject": {"type": "string"},
                },
            }

        # Translate simplified JSON schema to google schema type
        config_params["response_schema"] = genai.types.Schema(
            type=genai.types.Type.OBJECT,
            required=schema.get("required", []),
            properties={
                k: genai.types.Schema(type=genai.types.Type.STRING)
                for k in schema.get("properties", {}).keys()
            },
        )

        config = GenerateContentConfig(**config_params)

        response = await client.models.generate_content(
            model=model_name,
            contents=[Content(role="user", parts=[Part.from_text(text=prompt)])],
            config=config,
        )

        return response.parsed
