import os
from notion_client import AsyncClient
import logging
from datetime import datetime, time, timezone, timedelta

logger = logging.getLogger(__name__)

class NotionManager:
    @staticmethod
    async def get_latest_journal_entry(notion_token: str, database_id: str):
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
                        "timestamp": "last_edited_time",
                        "direction": "descending",
                    }
                ],
                filter={
                    "timestamp": "last_edited_time",
                    "last_edited_time": {
                        "on_or_after": last_24_hours_iso
                    }
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