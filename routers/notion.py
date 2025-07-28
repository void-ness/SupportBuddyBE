import httpx
import logging
from fastapi import APIRouter, HTTPException, status

from managers.notion_manager import NotionManager
from routers.validations.notion_validation import NotionAuthCode, Token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/notion/authorize", response_model=Token)
async def authorize_notion(auth_code: NotionAuthCode):
    try:
        result = await NotionManager().handle_notion_authorization(
            auth_code=auth_code.code
        )
        return result

    except httpx.HTTPStatusError as e:
        logger.error(f"Notion API response error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail="Error communicating with Notion API.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"An unexpected error occurred during Notion authorization: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected internal server error occurred.")

