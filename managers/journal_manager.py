from models.models import JournalEntry, Journal, Message, User
from managers.genai_manager import GenAIManager
from managers.email_manager import EmailManager
from managers.notion_manager import NotionManager
from managers.notion_integration_manager import NotionIntegrationManager
# from utils.database import get_db_connection
import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class JournalManager:
    def __init__(self):
        self.notion_integration_manager = NotionIntegrationManager()
        self.notion_manager = NotionManager()

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
    async def generate_motivational_message(journal_content: str) -> str:
        try:
            # Truncate journal_content to prevent abuse and manage costs
            MAX_JOURNAL_LENGTH = 2000
            if len(journal_content) > MAX_JOURNAL_LENGTH:
                journal_content = journal_content[:MAX_JOURNAL_LENGTH] + "... [Journal truncated]"

            with open("prompts/journal_prompt.md", "r") as f:
                system_prompt = f.read()
            
            message = await GenAIManager.generate(
                prompt=journal_content, 
                system_prompt=system_prompt
            )
            # print(f"Generated message: {message}")  # Debugging output
            return message
        except Exception as e:
            logger.error(f"Error generating motivational message: {e}")
            # Fallback to a static message
            import random
            fallback_messages = [
                "Hey, I hear you. It's completely understandable to feel overwhelmed and exhausted when you have a lot on your plate. Remember it's okay to rest and recharge. You don't have to do it all, all the time. Be kind to yourself and take a break.",
                "It sounds like you're carrying a really heavy load right now. It's completely valid to feel tired when you're trying to do so much. Maybe it's a good time to take a step back and see if there's anything you can delegate, postpone, or even let go of entirely. Your well-being is the most important thing. You deserve to rest and take care of yourself. Even small moments of self-care can make a difference. You've got this, and remember it's okay to ask for help if you need it."
            ]
            return random.choice(fallback_messages)

    async def process_and_email_user_journal(self, user: User):
        try:
            # 1. Get Notion integration details for the user asynchronously
            notion_integration = await self.notion_integration_manager.get_integration_by_user_id(user.id)
            if not notion_integration:
                logger.info(f"No Notion integration found for user {user.id}. Skipping.")
                return {"status": "No Notion integration found", "message": None}
            
            # print(f"Notion integration found for user {user.id}: {notion_integration}")  # Debugging output

            # 2. Fetch latest journal entry from Notion using user's credentials asynchronously
            journal_content = await self.notion_manager.get_latest_journal_entry(
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
            
            # 4. Send email to the user asynchronously
            await EmailManager.send_motivational_email(user.id, user.email, motivational_message, greeting="Hey,", salutation="Good morning!")

            logger.info(f"Successfully processed and emailed journal for user {user.id} ({user.email})")
            return {"status": "Journal processed and email sent", "message": motivational_message}
        except Exception as e:
            logger.error(f"Error processing and emailing journal for user {user.id} ({user.email}): {e}")
            raise
