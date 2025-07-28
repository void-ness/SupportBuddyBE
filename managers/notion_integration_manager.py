from typing import Optional
from datetime import datetime

from models.models import NotionIntegration
from utils.database import get_db_connection
from utils.utils import encrypt_data, decrypt_data

class NotionIntegrationManager:
    async def create_integration(self, user_id: int, access_token: str, page_id: str) -> NotionIntegration:
        conn = None
        try:
            conn = await get_db_connection()

            encrypted_access_token = encrypt_data(access_token)

            result = await conn.fetchrow(
                """INSERT INTO notion_integrations (user_id, access_token, page_id)
                   VALUES ($1, $2, $3) RETURNING id, created_at, updated_at""",
                user_id, encrypted_access_token, page_id
            )

            if result:
                return NotionIntegration(
                    id=result['id'],
                    user_id=user_id,
                    access_token=encrypted_access_token,
                    page_id=page_id,
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
            else:
                raise Exception("Failed to retrieve new Notion integration ID after insertion.")

        except Exception as e:
            raise Exception(f"Database error during Notion integration creation: {e}")
        finally:
            if conn:
                await conn.release()

    async def get_integration_by_user_id(self, user_id: int) -> Optional[NotionIntegration]:
        conn = None
        try:
            conn = await get_db_connection()
            integration_data = await conn.fetchrow("SELECT id, user_id, access_token, page_id, created_at, updated_at FROM notion_integrations WHERE user_id = $1", user_id)
            print(f"Fetched Notion integration data: {integration_data}")  # Debugging output
            if integration_data:
                decrypted_access_token = decrypt_data(integration_data["access_token"])
                return NotionIntegration(
                    id=integration_data["id"],
                    user_id=integration_data["user_id"],
                    access_token=decrypted_access_token,
                    page_id=integration_data["page_id"],
                    created_at=integration_data["created_at"],
                    updated_at=integration_data["updated_at"]
                )
            return None
        except Exception as e:
            raise Exception(f"Database error fetching Notion integration by user ID: {e}")
        finally:
            if conn:
                await conn.release()