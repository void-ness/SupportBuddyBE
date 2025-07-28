import os
from notion_client import Client
import logging
from datetime import datetime, time, timezone, timedelta

logger = logging.getLogger(__name__)

class NotionManager:
    @staticmethod
    def get_latest_journal_entry(notion_token: str, database_id: str):
        try:
            if not notion_token or not database_id:
                raise Exception("Notion token or database ID not provided.")

            notion = Client(auth=notion_token)

            # Query the database
            response = notion.databases.query(
                database_id=database_id,
                sorts=[
                    {
                        "timestamp": "last_edited_time",
                        "direction": "descending",
                    }
                ],
                page_size=1
            )
            print(response)
            
            if response["results"]:
                latest_journal_page = response["results"][0]
                
                # Fetch content of the latest journal page
                content_blocks = notion.blocks.children.list(block_id=latest_journal_page["id"])
                print(content_blocks)
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
