from google import genai
from google.genai import Client
from google.genai.types import GenerateContentConfig
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GenAIManager:
    @classmethod
    async def generate(cls, prompt: str, system_prompt: str = None):
        api_key = os.getenv('GOOGLE_GENAI_API_KEY')
        model_name = os.getenv('GOOGLE_GENAI_MODEL', 'gemini-2.5-flash') # Use env variable
        client = Client(api_key=api_key)

        config = None
        if system_prompt:
            config = GenerateContentConfig(
                system_instruction=[system_prompt]
            )

        response = client.models.generate_content(
            model=model_name,
            contents=[prompt],
            config=config,
        )
        return response.text