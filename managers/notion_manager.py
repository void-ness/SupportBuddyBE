import os
from notion_client import Client
import logging
from datetime import datetime, time, timezone, timedelta

logger = logging.getLogger(__name__)

class NotionManager:
    @staticmethod
    def get_latest_journal_entry(notion_token: str, parent_page_id: str):
        try:
            if not notion_token or not parent_page_id:
                raise Exception("Notion token or parent page ID not provided.")

            notion = Client(auth=notion_token)

            def _normalize_id(notion_id: str) -> str:
                return notion_id.replace("-", "")

            # Use notion.search to find the latest child page
            response = notion.search(
                filter={
                    "property": "object",
                    "value": "page"
                },
                sort={
                    "direction": "descending",
                    "timestamp": "last_edited_time"
                },
                page_size=1
            )

            latest_journal_page = None
            if response["results"]:
                # Check if the found page is a child of the specified parent_page_id
                # and if it was created within the last 24 hours.
                page_details = response["results"][0]
                
                # Ensure it's a child of the correct parent page
                if page_details.get("parent") and page_details["parent"].get("type") == "page_id" and _normalize_id(page_details["parent"]["page_id"]) == _normalize_id(parent_page_id):
                    created_time_str = page_details.get("created_time")
                    if created_time_str:
                        created_time = datetime.fromisoformat(created_time_str.replace('Z', '+00:00'))
                        time_24_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)
                        if created_time > time_24_hours_ago:
                            latest_journal_page = page_details
            
            if latest_journal_page:
                # Fetch content of the latest journal page
                content_blocks = notion.blocks.children.list(block_id=latest_journal_page["id"])
                journal_content = ""
                for block in content_blocks["results"]:
                    if "paragraph" in block and block["paragraph"]["rich_text"]:
                        for text_obj in block["paragraph"]["rich_text"]:
                            journal_content += text_obj["plain_text"]
                    elif "heading_1" in block and block["heading_1"]["rich_text"]:
                        for text_obj in block["heading_1"]["rich_text"]:
                            journal_content += text_obj["plain_text"]
                    elif "heading_2" in block and block["heading_2"]["rich_text"]:
                        for text_obj in block["heading_2"]["rich_text"]:
                            journal_content += text_obj["plain_text"]
                    elif "heading_3" in block and block["heading_3"]["rich_text"]:
                        for text_obj in block["heading_3"]["rich_text"]:
                            journal_content += text_obj["plain_text"]
                    # Add more block types as needed (e.g., bulleted_list, numbered_list)

                # print(f"Latest journal entry content: {journal_content}")
                return journal_content
            else:
                return None

        except Exception as e:
            logger.error(f"Error fetching from Notion: {e}")
            return None
