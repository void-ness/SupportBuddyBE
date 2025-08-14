from google import genai
from google.genai.types import GenerateContentConfig, HttpOptions, HttpRetryOptions
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv()

class GenAIManager:
    _client = None
    
    @classmethod
    def _get_client(cls):
        if cls._client is None:
            api_key = os.getenv('GOOGLE_GENAI_API_KEY')
            
            # Configure HTTP options with retry and timeout settings
            retry_options = HttpRetryOptions(
                attempts=3,          # Maximum number of attempts (including original)
                initial_delay=1.0,   # Initial delay in seconds
                max_delay=10.0,      # Maximum delay in seconds  
                exp_base=2.0,        # Exponential backoff multiplier
                jitter=0.1           # Randomness factor for delay
            )
            
            http_options = HttpOptions(
                timeout=60*1000,  # 60 seconds (in ms) timeout
                retry_options=retry_options,
                api_version='v1beta'
            )
            
            # Create a regular client first, then access its async client
            sync_client = genai.Client(
                api_key=api_key,
                http_options=http_options
            )
            cls._client = sync_client.aio
        return cls._client
    
    @classmethod
    async def generate(cls, prompt: str, system_prompt: str = None):
        model_name = os.getenv('GOOGLE_GENAI_MODEL', 'gemini-2.5-flash')
        client = cls._get_client()

        config = None
        if system_prompt:
            config = GenerateContentConfig(
                system_instruction=[system_prompt]
            )

        response = await client.models.generate_content(
            model=model_name,
            contents=[prompt],
            config=config,
        )

        usage_meta = response.usage_metadata
        logger.info("Usage Metadata: %s", usage_meta)

        return response.text
    
    @classmethod
    async def get_model_info(cls, model_name: str = None):
        """Get information about the GenAI model"""
        if model_name is None:
            model_name = os.getenv('GOOGLE_GENAI_MODEL', 'gemini-2.5-flash')
        
        client = cls._get_client()
        
        try:
            # Get model details
            model_info = await client.models.get(model=model_name)
            return {
                "model_name": model_name,
                "model_info": model_info.model_dump(exclude_none=True)
            }
        except Exception as e:
            return {
                "model_name": model_name,
                "error": str(e),
                "available_models": await cls._get_available_models()
            }
    
    @classmethod
    async def _get_available_models(cls):
        """Get list of available models"""
        try:
            client = cls._get_client()
            models = await client.models.list()
            return [model.name for model in models]
        except Exception as e:
            return [f"Error fetching models: {str(e)}"]