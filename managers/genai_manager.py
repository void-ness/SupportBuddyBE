from google import genai
from google.genai import Client, types
from google.genai.types import Content
import os
from dotenv import load_dotenv

from models import PredictionOutput

# Load environment variables
load_dotenv()

# class PredictionOut

class GenAIManager:   
    @classmethod
    async def generate(cls, prompt: str):
        api_key = os.getenv('GOOGLE_GENAI_API_KEY')
        client = Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=[prompt],
            config={
                "response_mime_type": "application/json",
                "response_schema": PredictionOutput
            }
        )
        return response.parsed