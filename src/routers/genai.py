from fastapi import APIRouter, HTTPException
from managers.genai_manager import GenAIManager
import logging
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/model-info")
async def get_model_info(model_name: str = None):
    """
    Get information about the GenAI model.
    """
    try:
        info = await GenAIManager.get_model_info(model_name)
        return {
            "environment": os.getenv('ENVIRONMENT', 'production'),
            "current_model": os.getenv('GOOGLE_GENAI_MODEL', 'gemini-2.5-flash'),
            "model_details": info
        }
    except Exception as e:
        logger.error(f"Error fetching model info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch model info: {e}")

@router.get("/available-models")
async def get_available_models():
    """
    Get list of available GenAI models.
    """
    try:
        models = await GenAIManager._get_available_models()
        return {
            "environment": os.getenv('ENVIRONMENT', 'production'),
            "available_models": models
        }
    except Exception as e:
        logger.error(f"Error fetching available models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch available models: {e}")

@router.post("/test-generate")
async def test_generate(prompt: str, system_prompt: str = None):
    """
    Test text generation with the GenAI model.
    """
    try:
        response = await GenAIManager.generate(prompt, system_prompt)
        return {
            "model_used": os.getenv('GOOGLE_GENAI_MODEL', 'gemini-2.5-flash'),
            "prompt": prompt,
            "system_prompt": system_prompt,
            "response": response
        }
    except Exception as e:
        logger.error(f"Error testing generation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test generation: {e}")

@router.get("/health")
async def genai_health():
    """
    Check GenAI service health.
    """
    try:
        # Test with a simple prompt
        test_response = await GenAIManager.generate("Hello", "Respond with a single word: 'OK'")
        return {
            "environment": os.getenv('ENVIRONMENT', 'production'),
            "status": "healthy",
            "model": os.getenv('GOOGLE_GENAI_MODEL', 'gemini-2.5-flash'),
            "test_response": test_response,
            "api_key_configured": bool(os.getenv('GOOGLE_GENAI_API_KEY'))
        }
    except Exception as e:
        logger.error(f"GenAI health check failed: {e}")
        return {
            "environment": os.getenv('ENVIRONMENT', 'production'),
            "status": "unhealthy",
            "error": str(e),
            "api_key_configured": bool(os.getenv('GOOGLE_GENAI_API_KEY'))
        }
