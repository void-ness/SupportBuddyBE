from models.models import JournalEntry, Journal, User, NotionJournalEntry

from managers.genai_manager import GenAIManager
from managers.email_manager import EmailManager
from managers.notion_module.notion_manager import NotionManager
from managers.notion_integration_manager import NotionIntegrationManager
# from utils.database import get_db_connection

import logging
import asyncio
import json
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configuration constants
GENAI_MAX_RETRIES = 1  # Number of retries for AI message generation
MAX_JOURNAL_LENGTH = 2000  # Maximum length for journal content in prompt

class JournalManager:
    def __init__(self):
        self.notion_integration_manager = NotionIntegrationManager()

    #todo - refactor this to use async database connection of tortoise ORM
    @staticmethod
    async def create_journal_entry(journal_entry: JournalEntry) -> Journal:
        conn = None
        try:
            conn = await get_db_connection()

            new_entry_data = await conn.fetchrow(
                """
                INSERT INTO journal_entries (user_id, content)
                VALUES ($1, $2)
                RETURNING id, user_id, content, created_at
                """,
                journal_entry.user_id, journal_entry.content,
            )

            if new_entry_data:
                journal = Journal(
                    id=new_entry_data['id'],
                    user_id=new_entry_data['user_id'],
                    content=new_entry_data['content'],
                    created_at=new_entry_data['created_at'],
                )

                # run the message generation asynchronously in background
                asyncio.create_task(
                    JournalManager.generate_motivational_message(journal.content)
                )

                return journal
            else:
                raise Exception("Failed to create journal entry.")

        except Exception as e:
            logger.error(f"Error creating journal entry: {e}")
            raise
        finally:
            if conn:
                await conn.release()

    @staticmethod
    def _truncate_journal_for_prompt(journal_content: NotionJournalEntry, max_length: int) -> str:
        """
        Truncates journal content to a max length, ensuring valid JSON.
        It proportionally shortens fields if the total length exceeds the limit.
        """
        # Get the journal data as a dictionary, excluding empty fields
        journal_data = journal_content.model_dump(exclude_none=True)
        
        content_values = [v for v in journal_data.values() if isinstance(v, str)]
        content_len = sum(len(v) for v in content_values)
    
        if content_len > max_length:            
            # Calculate how much we need to trim
            overflow = content_len - max_length
            
            if content_len > 0:
                # Trim each value proportionally
                for key, value in journal_data.items():
                    if isinstance(value, str):
                        # Calculate how much to remove from this specific field
                        proportion = len(value) / content_len
                        # Subtract 18 to account for adding "... (truncated)"
                        truncation_amount = int(overflow * proportion) + 18 
                        
                        if truncation_amount < len(value):
                            new_len = len(value) - truncation_amount
                            journal_data[key] = value[:new_len] + "... (truncated)"
                        else:
                            # If the field is too small to truncate meaningfully, keep it as it is
                            journal_data[key] = value
            
            # Remove any fields that became empty after truncation
            journal_data = {k: v for k, v in journal_data.items() if v}

        # Create the final JSON prompt, pretty-printed
        return json.dumps(journal_data, indent=2)

    @staticmethod
    async def generate_motivational_message(journal_content: NotionJournalEntry) -> str:
        final_prompt = JournalManager._truncate_journal_for_prompt(
            journal_content, MAX_JOURNAL_LENGTH
        )

        with open("prompts/journal_prompt.md", "r") as f:
            system_prompt = f.read()
        
        for attempt in range(GENAI_MAX_RETRIES + 1):  # Initial attempt + retries
            try:
                message = await GenAIManager.generate(
                    prompt=final_prompt, 
                    system_prompt=system_prompt
                )
                
                # Check if message is empty or None
                if message and message.strip():
                    logger.info(f"Successfully generated motivational message on attempt {attempt + 1}")
                    return message
                else:
                    if attempt < GENAI_MAX_RETRIES:
                        logger.warning(f"Generated message is empty or None on attempt {attempt + 1}. Retrying...")
                        await asyncio.sleep(1)  # Brief delay before retry
                        continue
                    else:
                        logger.error(f"Generated message is empty or None after {GENAI_MAX_RETRIES + 1} attempts. Using fallback message.")
                        break
                        
            except Exception as e:
                if attempt < GENAI_MAX_RETRIES:
                    logger.warning(f"Error generating motivational message on attempt {attempt + 1}: {e}. Retrying...")
                    await asyncio.sleep(1)  # Brief delay before retry
                    continue
                else:
                    logger.error(f"Error generating motivational message after {GENAI_MAX_RETRIES + 1} attempts: {e}. Using fallback message.")
                    break
        
        # Fallback to a static message if all attempts failed
        fallback_messages = [
            "Hey, I hear you. It's completely understandable to feel overwhelmed and exhausted when you have a lot on your plate. Remember it's okay to rest and recharge. You don't have to do it all, all the time. Be kind to yourself and take a break.",
            "It sounds like you're carrying a really heavy load right now. It's completely valid to feel tired when you're trying to do so much. Maybe it's a good time to take a step back and see if there's anything you can delegate, postpone, or even let go of entirely. Your well-being is the most important thing. You deserve to rest and take care of yourself. Even small moments of self-care can make a difference. You've got this, and remember it's okay to ask for help if you need it."
        ]
        selected_fallback = random.choice(fallback_messages)
        logger.info("Using fallback motivational message")
        return selected_fallback

    async def process_and_email_user_journal(self, user: User):
        try:
            # 1. Get Notion integration details for the user asynchronously
            notion_integration = await self.notion_integration_manager.get_integration_by_user_id(user.id)
            if not notion_integration:
                logger.info(f"No Notion integration found for user {user.id}. Skipping.")
                return {"status": "No Notion integration found", "message": None}
            
            # print(f"Notion integration found for user {user.id}: {notion_integration}")  # Debugging output

            notion_manager: NotionManager = NotionManager.get_manager_by_integration(notion_integration)

            # 2. Fetch latest journal entry from Notion using user's credentials asynchronously
            journal_content = await notion_manager.get_latest_journal_entry(
                notion_token=notion_integration.access_token,
                database_id=notion_integration.page_id
            )

            # print(f"Fetched journal content: {journal_content}")  # Debugging output

            if not journal_content:
                user.inactive_days_counter += 1
                await user.save(update_fields=["inactive_days_counter", "updated_at"])
                logger.info(f"No journal entry for user {user.id} from the last 24 hours. Incremented inactive counter to {user.inactive_days_counter}.")
                return {"status": "No journal entry found from the last 24 hours.", "message": None}

            # If content is found, reset the counter if it's not already zero
            if user.inactive_days_counter > 0:
                user.inactive_days_counter = 0
                await user.save(update_fields=["inactive_days_counter", "updated_at"])
                logger.info(f"Journal entry found for user {user.id}. Reset inactive counter to 0.")

            # 3. Generate motivational message asynchronously
            motivational_message = await JournalManager.generate_motivational_message(journal_content)
            
            # Validate that we have a valid message before sending email
            if not motivational_message or not motivational_message.strip():
                logger.error(f"Generated message is empty or None for user {user.id}. Cannot send email.")
                return {"status": "Failed to generate motivational message", "message": None}
            
            # 4. Send email to the user asynchronously
            await EmailManager.send_motivational_email(user.id, user.email, motivational_message, greeting="Hey,", salutation="Good morning!")

            logger.info(f"Successfully processed and emailed journal for user {user.id} ({user.email})")
            return {"status": "Journal processed and email sent", "message": motivational_message}
        except Exception as e:
            logger.error(f"Error processing and emailing journal for user {user.id} ({user.email}): {e}")
            raise  