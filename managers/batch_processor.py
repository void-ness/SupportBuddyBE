import asyncio
import logging
from typing import List
import os

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
        active_notion_users = await self.user_manager.get_active_notion_users()
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

    async def process_user_deactivation(self):
        """
        Processes the deactivation of users who have been inactive for too long.
        """
        logger.info("Starting user deactivation process.")
        try:
            # Get threshold from environment variable, with a default
            inactivity_threshold = int(os.environ.get("INACTIVITY_THRESHOLD_DAYS", 30))
            
            deactivated_count = await self.user_manager.deactivate_long_inactive_users(inactivity_threshold)
            
            if deactivated_count > 0:
                logger.info(f"Successfully deactivated {deactivated_count} inactive users.")
            else:
                logger.info("No users met the criteria for deactivation.")
                
        except Exception as e:
            logger.error(f"An error occurred during the user deactivation process: {e}")

        logger.info("Finished user deactivation process.")
