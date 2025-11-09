from typing import Optional
from datetime import datetime

from models.models import NotionIntegration, NotionIntegrationPydantic
from utils.utils import encrypt_data, decrypt_data

class NotionIntegrationManager:
    async def create_integration(self, user_id: int, access_token: str, page_id: str, version: str = "v1") -> NotionIntegrationPydantic:
        try:
            encrypted_access_token = encrypt_data(access_token)
            integration = await NotionIntegration.create(
                user_id=user_id,
                access_token=encrypted_access_token,
                page_id=page_id,
                version=version
            )
            return integration.to_pydantic()
        except Exception as e:
            raise Exception(f"Database error during Notion integration creation: {e}")

    async def get_integration_by_user_id(self, user_id: int) -> Optional[NotionIntegrationPydantic]:
        try:
            integration = await NotionIntegration.filter(user_id=user_id).order_by("-created_at").first()
            
            if integration:
                decrypted_access_token = decrypt_data(integration.access_token)
                integration.access_token = decrypted_access_token # Update the model instance for return
                return integration.to_pydantic()
            return None
        except Exception as e:
            raise Exception(f"Database error fetching Notion integration by user ID: {e}")