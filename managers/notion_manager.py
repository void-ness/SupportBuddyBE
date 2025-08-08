import os
from notion_client import AsyncClient
import logging
from datetime import datetime, time, timezone, timedelta
import httpx
import base64

from managers.notion_integration_manager import NotionIntegrationManager
from managers.user_manager import UserManager
from utils.utils import create_access_token # Import create_access_token

logger = logging.getLogger(__name__)

class NotionManager:
    NOTION_CLIENT_ID = os.getenv("NOTION_CLIENT_ID")
    NOTION_CLIENT_SECRET = os.getenv("NOTION_CLIENT_SECRET")
    NOTION_REDIRECT_URI = os.getenv("NOTION_REDIRECT_URI")

    def __init__(self):
        self.notion_integration_manager = NotionIntegrationManager()
        self.user_manager = UserManager()

    async def get_latest_journal_entry(self, notion_token: str, database_id: str):
        try:
            if not notion_token or not database_id:
                raise Exception("Notion token or database ID not provided.")

            notion = AsyncClient(auth=notion_token)

            # Calculate timestamp for 24 hours ago
            last_24_hours = datetime.now(timezone.utc) - timedelta(hours=24)
            last_24_hours_iso = last_24_hours.isoformat()

            # Query the database
            response = await notion.databases.query(
                database_id=database_id,
                sorts=[
                    {
                        "timestamp": "created_time",
                        "direction": "descending",
                    }
                ],
                filter={
                   "and":
                        [
                            {
                                "property": "Ignore This",
                                "checkbox": {
                                    "equals": False
                                }
                            },
                            {
                                "timestamp": "last_edited_time",
                                "last_edited_time": {
                                    "on_or_after": last_24_hours_iso
                                }
                            }
                        ]
                },
                page_size=1
            )            
            if response["results"]:
                latest_journal_page = response["results"][0]
                
                journal_content = []
                properties = latest_journal_page["properties"]

                # Extract Entry Title
                entry_title = properties.get('Entry Title', {}).get('title', [])
                if entry_title:
                    title_text = entry_title[0].get('plain_text', '')
                    if title_text:  # Only add if title_text is not empty
                        journal_content.append(f"Entry Title - {title_text}")

                # Extract rich text properties
                rich_text_properties = ['Gratitude', 'Highlights', 'Challenges', 'Reflection']
                for prop_name in rich_text_properties:
                    prop_data = properties.get(prop_name, {}).get('rich_text', [])
                    if prop_data:
                        content_text = "".join([text_obj.get('plain_text', '') for text_obj in prop_data])
                        if content_text:  # Only add if content_text is not empty
                            journal_content.append(f"{prop_name} - {content_text}")
                
                result = "\n".join(journal_content)
                if not result.strip():  # Check if the joined string is empty or only contains whitespace
                    return None
                return result
            else:
                return None

        except Exception as e:
            logger.error(f"Error fetching from Notion: {e}")
            return None

    async def _exchange_code_for_token(self, auth_code: str) -> dict:
        try:
            client_id = self.NOTION_CLIENT_ID
            client_secret = self.NOTION_CLIENT_SECRET
            redirect_uri = self.NOTION_REDIRECT_URI

            if not any([client_id, client_secret, redirect_uri]):
                raise ValueError("Notion API credentials not configured.")
            
            token_url = "https://api.notion.com/v1/oauth/token"
            auth_string = f"{client_id}:{client_secret}"
            encoded_auth_string = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

            headers = {
                "Authorization": f"Basic {encoded_auth_string}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            }

            payload = {
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": redirect_uri
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data
        except httpx.HTTPStatusError as e:
            logger.error(f"Notion API response error: {e.response.status_code} - {e.response.text}")
            raise Exception("Failed to authenticate with Notion. Please try again later.")
        except Exception as e:
            logger.exception(f"Error while authorizing with Notion: {str(e)}")
            raise Exception("Failed to authenticate with Notion. Please try again later.")

    async def handle_notion_authorization(self, auth_code: str):
        data = await self._exchange_code_for_token(
            auth_code=auth_code
        )

        access_token = data.get("access_token")
        duplicated_template_id = data.get("duplicated_template_id")
        owner_info = data.get("owner", {})
        user_email = owner_info.get("user", {}).get("person", {}).get("email")

        if not access_token:
            raise ValueError("Failed to get access token from Notion.")

        if not duplicated_template_id:
            raise ValueError("Failed to get template ID from Notion. Please select duplicate the template while authenticating with Notion.")

        if not user_email:
            raise ValueError("Failed to get user email from Notion.")

        user, created = await self.user_manager.get_or_create_user_by_email(user_email)

        await self.notion_integration_manager.create_integration(
            user_id=user.id,
            access_token=access_token,
            page_id=duplicated_template_id
        )

        app_access_token = create_access_token(data={"sub": str(user.id)})
        return {
            "access_token": app_access_token, 
            "token_type": "bearer",
            "existing_user": not created
        }