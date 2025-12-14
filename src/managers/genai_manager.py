import os
import logging
from pathlib import Path

from dotenv import load_dotenv

from managers.genai_providers import GenAIProviderName, get_provider
from managers.genai_providers.base import GenerationParams

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv()


class GenAIManager:
    """Facade for generating text/JSON using a selected LLM provider.

    You can choose the provider at call-site using `provider="google"` or
    `provider="amazon"` (Bedrock).

    If omitted, provider falls back to `GENAI_PROVIDER` env var, then "google".
    """

    @classmethod
    def _resolve_provider(cls, provider: GenAIProviderName | None) -> GenAIProviderName:
        if provider:
            return provider
        return os.getenv("GENAI_PROVIDER", "google")  # type: ignore[return-value]

    @classmethod
    async def generate(
        cls,
        prompt: str,
        system_prompt: str = None,
        model_name: str = None,
        provider: GenAIProviderName | None = None,
    ):
        provider_name = cls._resolve_provider(provider)
        provider_impl = get_provider(provider_name)

        text = await provider_impl.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            model_name=model_name,
            params=GenerationParams(temperature=1.5, max_output_tokens=3000),
        )
        return text
    
    @classmethod
    async def generate_json(
        cls,
        prompt: str,
        system_prompt: str = None,
        provider: GenAIProviderName | None = None,
        model_name: str | None = None,
    ):
        provider_name = cls._resolve_provider(provider)
        provider_impl = get_provider(provider_name)

        # Default reminder model is provider-specific; for google keep existing env var.
        if provider_name == "google":
            model_name = model_name or os.getenv(
                "GOOGLE_GENAI_MODEL_REMINDER", "gemini-flash-latest"
            )

        parsed = await provider_impl.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            model_name=model_name,
            schema={
                "type": "object",
                "required": ["message", "subject"],
                "properties": {
                    "message": {"type": "string"},
                    "subject": {"type": "string"},
                },
            },
            params=GenerationParams(temperature=1.5, max_output_tokens=3000),
        )
        return parsed

    @classmethod
    async def generate_email_subject(
        cls,
        journal_entry: str,
        generated_reply: str,
        provider: GenAIProviderName | None = None,
    ) -> str:
        """
        Generates a catchy email subject based on the journal entry.
        """
        try:
            # Use absolute path based on current file location
            base_dir = Path(__file__).parent.parent
            subject_prompt_path = base_dir / "prompts" / "email_subject_prompt.md"
            system_prompt_path = base_dir / "prompts" / "email_subject_system_prompt.md"

            with open(subject_prompt_path, "r", encoding="utf-8") as f:
                user_prompt_template = f.read()

            with open(system_prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read()
            
            prompt = user_prompt_template.replace("{{user_entry}}", journal_entry).replace("{{reply_generated}}", generated_reply)
            model_name = None
            if cls._resolve_provider(provider) == "google":
                model_name = os.getenv("GOOGLE_GENAI_MODEL_EMAIL_SUBJECT", "gemini-2.5-flash")
            
            subject = await cls.generate(
                prompt,
                system_prompt,
                model_name=model_name,
                provider=provider,
            )
            return subject.strip() if subject else "Your Daily Motivational Message"
        except Exception as e:
            logger.error(f"Error generating email subject: {e}")
            return "Your Daily Motivational Message"
        
    @classmethod
    async def generate_reminder_mail_data(
        cls,
        last_journal_entry: str = "",
        inactive_days: int = 0,
        provider: GenAIProviderName | None = None,
    ) -> tuple[str, str]:
        """
        Generates a reminder email info based on the last journal entry and inactive days.
        """
        try:
            # Use absolute path based on current file location
            base_dir = Path(__file__).parent.parent
            subject_prompt_path = base_dir / "prompts" / "reminder_message_prompt.md"
            system_prompt_path = base_dir / "prompts" / "reminder_message_system_prompt.md"

            with open(subject_prompt_path, "r", encoding="utf-8") as f:
                user_prompt_template = f.read()

            with open(system_prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read()
            
            prompt = user_prompt_template.replace("{{user_entry}}", last_journal_entry).replace("{{inactive_days}}", str(inactive_days))

            response = await cls.generate_json(
                prompt,
                system_prompt,
                provider=provider,
            )
            message = response["message"].strip() if "message" in response else "JurnAI misses you! It's been a while since your last journal entry. Remember, journaling can be a great way to reflect and stay motivated. I encourage you to write something today!"
            subject = response["subject"].strip() if "subject" in response else "Long Time No Journalling :("
            return message, subject
        except Exception as e:
            logger.error(f"Error generating reminder email message and subject: {e}")
            raise

    @classmethod
    async def get_model_info(cls, model_name: str = None):
        """Get information about the GenAI model"""
        # Provider-specific model introspection is only implemented for Google for now.
        provider_name = cls._resolve_provider(None)
        if provider_name != "google":
            return {
                "provider": provider_name,
                "model_name": model_name or os.getenv("BEDROCK_MODEL_ID"),
                "note": "Model introspection not supported for this provider yet.",
            }

        # Lazy import to keep non-google deployments light.
        from managers.genai_providers.google_provider import GoogleGenAIProvider

        if model_name is None:
            model_name = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.5-flash")

        client = GoogleGenAIProvider._get_client()

        try:
            model_info = await client.models.get(model=model_name)
            return {
                "provider": provider_name,
                "model_name": model_name,
                "model_info": model_info.model_dump(exclude_none=True),
            }
        except Exception as e:
            return {
                "provider": provider_name,
                "model_name": model_name,
                "error": str(e),
                "available_models": await cls._get_available_models(),
            }

    @classmethod
    async def _get_available_models(cls):
        """Get list of available models"""
        provider_name = cls._resolve_provider(None)
        if provider_name != "google":
            return ["Model listing not supported for this provider"]

        try:
            from managers.genai_providers.google_provider import GoogleGenAIProvider

            client = GoogleGenAIProvider._get_client()
            models = await client.models.list()
            return [model.name for model in models]
        except Exception as e:
            return [f"Error fetching models: {str(e)}"]
