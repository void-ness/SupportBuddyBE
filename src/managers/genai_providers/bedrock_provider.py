from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional

import boto3

from .base import GenAIProvider, GenerationParams

logger = logging.getLogger(__name__)


def _coalesce(*values):
    for v in values:
        if v is not None and v != "":
            return v
    return None


class BedrockProvider(GenAIProvider):
    """Amazon Bedrock provider.

    Uses the bedrock-runtime `converse` API where available.

    Env vars used:
    - AWS_REGION (or AWS_DEFAULT_REGION)
    - AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_SESSION_TOKEN (optional if instance profile)
    - BEDROCK_MODEL_ID (default model)

    Notes:
    - Bedrock doesn't have a universal JSON-schema mode across all models.
      For `generate_json` we instruct the model to return strict JSON and
      then parse it.
    """

    _client = None

    @classmethod
    def _get_client(cls):
        if cls._client is None:
            region = _coalesce(os.getenv("AWS_REGION"), os.getenv("AWS_DEFAULT_REGION"), "us-east-1")
            cls._client = boto3.client("bedrock-runtime", region_name=region)
        return cls._client

    def _build_messages(self, prompt: str, system_prompt: Optional[str]):
        # Bedrock converse expects list of message blocks
        messages = []
        if system_prompt:
            # Some models support system as a separate field; we include as a system message for broad compatibility
            messages.append({"role": "system", "content": [{"text": system_prompt}]})
        messages.append({"role": "user", "content": [{"text": prompt}]})
        return messages

    async def _converse(self, *, model_id: str, messages, temperature: float, max_tokens: int) -> str:
        client = self._get_client()

        def _call():
            # Use converse for modern Bedrock models (Claude 3+, Llama 3.1, etc.)
            return client.converse(
                modelId=model_id,
                messages=messages,
                inferenceConfig={
                    "maxTokens": max_tokens,
                    "temperature": temperature,
                },
            )

        resp = await asyncio.to_thread(_call)
        output = resp.get("output", {})
        message = output.get("message", {})
        content = message.get("content", [])
        # content is list of blocks like {"text": "..."}
        text_parts = [c.get("text", "") for c in content if isinstance(c, dict)]
        return "".join(text_parts).strip()

    async def _generate_text_impl(
        self,
        *,
        prompt: str,
        system_prompt: Optional[str],
        model_name: Optional[str],
        params: GenerationParams,
    ) -> str:
        model_id = model_name or os.getenv("BEDROCK_MODEL_ID")
        if not model_id:
            raise RuntimeError("BEDROCK_MODEL_ID must be set or model_name provided")

        messages = self._build_messages(prompt, system_prompt)
        text = await self._converse(
            model_id=model_id,
            messages=messages,
            temperature=params.temperature,
            max_tokens=params.max_output_tokens,
        )
        logger.info("Bedrock generation completed")
        return text

    async def _generate_json_impl(
        self,
        *,
        prompt: str,
        system_prompt: Optional[str],
        model_name: Optional[str],
        schema: Optional[Dict[str, Any]],
        params: GenerationParams,
    ) -> Dict[str, Any]:
        # Instruct strict JSON. Keep schema simple.
        if schema is None:
            schema = {
                "type": "object",
                "required": ["message", "subject"],
                "properties": {
                    "message": {"type": "string"},
                    "subject": {"type": "string"},
                },
            }

        schema_hint = json.dumps(schema, ensure_ascii=False)
        json_instruction = (
            "Return ONLY valid minified JSON. No markdown, no code fences. "
            f"It must conform to this JSON schema: {schema_hint}"
        )

        combined_system = (system_prompt + "\n\n" if system_prompt else "") + json_instruction

        text = await self._generate_text_impl(
            prompt=prompt,
            system_prompt=combined_system,
            model_name=model_name,
            params=params,
        )

        # Try direct parse first; if model adds leading/trailing text, try to extract JSON object.
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                candidate = text[start : end + 1]
                return json.loads(candidate)
            raise
