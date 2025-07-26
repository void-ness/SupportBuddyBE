import os
import requests
import base64
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from managers.notion_integration_manager import NotionIntegrationManager
from managers.user_manager import UserManager
from utils.utils import create_access_token

router = APIRouter()
logger = logging.getLogger(__name__)

notion_integration_manager = NotionIntegrationManager()
user_manager = UserManager()

NOTION_CLIENT_ID = os.getenv("NOTION_CLIENT_ID")
NOTION_CLIENT_SECRET = os.getenv("NOTION_CLIENT_SECRET")
NOTION_REDIRECT_URI = os.getenv("NOTION_REDIRECT_URI")

class NotionAuthCode(BaseModel):
    code: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/notion/authorize", response_model=Token)
async def authorize_notion(auth_code: NotionAuthCode):
    if not NOTION_CLIENT_ID or not NOTION_CLIENT_SECRET or not NOTION_REDIRECT_URI:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Notion API credentials not configured.")

    # --- Correctly implement HTTP Basic Authentication ---
    # 1. Combine client ID and secret, delimited by a colon
    auth_string = f"{NOTION_CLIENT_ID}:{NOTION_CLIENT_SECRET}"
    # 2. Base64 encode the combined string
    encoded_auth_string = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

    token_url = "https://api.notion.com/v1/oauth/token"
    
    headers = {
        "Authorization": f"Basic {encoded_auth_string}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"  
    }
    
    # The payload no longer contains client_id or client_secret
    payload = {
        "grant_type": "authorization_code",
        "code": auth_code.code,
        "redirect_uri": NOTION_REDIRECT_URI
    }

    try:
        print(token_url, headers, payload)
        response = requests.post(token_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        # data = {
        #     "access_token": "mock_access_token",
        #     "duplicated_template_id": "mock_template_id",
        #     "owner": {
        #         "user": {
        #             "person": {
        #                 "email": "demo1@gmail.com"
        #             }
        #         }
        #     }
        # }

        access_token = data.get("access_token")
        duplicated_template_id = data.get("duplicated_template_id")
        owner_info = data.get("owner", {})
        user_email = owner_info.get("user", {}).get("person", {}).get("email")

        if not access_token or not duplicated_template_id or not user_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get access token, duplicated template ID, or user email from Notion.")

        # Get or create user based on Notion email
        user = user_manager.get_or_create_user_by_email(user_email)

        # Save the Notion integration for the current user
        notion_integration_manager.create_integration(
            user_id=user.id,
            access_token=access_token,
            page_id=duplicated_template_id
        )

        # Update user's journal_medium to 'notion'
        user_manager.update_user_journal_medium(user.id, "notion")

        # Generate and return our application's JWT
        app_access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": app_access_token, "token_type": "bearer"}

    except requests.exceptions.RequestException as e:
        # Log the detailed error response from Notion
        if e.response is not None:
            logger.error(f"Notion API response error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error communicating with Notion API: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")

