import asyncio
import logging
from typing import List

from managers.user_manager import UserManager
from managers.journal_manager import JournalManager
from models.models import User

logger = logging.getLogger(__name__)

class BatchProcessor:
    def __init__(self):
        self.user_manager = UserManager()
        self.journal_manager = JournalManager()

    async def process_notion_users_in_batches(self, batch_size: int = 5):
        logger.info("Starting batch processing for Notion users.")
        active_notion_users = self.user_manager.get_active_notion_users()
        logger.info(f"Found {len(active_notion_users)} active Notion users.")

        if not active_notion_users:
            logger.info("No active Notion users to process.")
            return

        for i in range(0, len(active_notion_users), batch_size):
            batch = active_notion_users[i:i + batch_size]
            tasks = []
            for user in batch:
                logger.info(f"Adding task for user {user.id} ({user.email})")
                tasks.append(self.journal_manager.process_and_email_user_journal(user))
            
            # Run tasks concurrently for the current batch
            await asyncio.gather(*tasks, return_exceptions=True) # return_exceptions to prevent one failure from stopping others
            logger.info(f"Processed batch {i // batch_size + 1}.")

        logger.info("Finished batch processing for Notion users.")
