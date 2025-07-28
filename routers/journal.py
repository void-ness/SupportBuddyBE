from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from models.models import JournalEntry, Journal
from managers.journal_manager import JournalManager
from managers.notion_manager import NotionManager
from managers.notion_integration_manager import NotionIntegrationManager
from managers.email_manager import EmailManager
import logging
import os
from dotenv import load_dotenv
load_dotenv()

class EmailRequest(BaseModel):
    to_email: str
    message: str

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/journal/", response_model=Journal)
async def create_journal(journal_entry: JournalEntry):
    try:
        new_journal_entry = await JournalManager.create_journal_entry(journal_entry)
        return new_journal_entry
    except Exception as e:
        logger.error(f"Error creating journal entry: {e}")
        raise HTTPException(status_code=500, detail="Failed to create journal entry.")

@router.post("/generate-message/")
async def generate_message(journal_entry: JournalEntry):
    try:
        message = await JournalManager.generate_motivational_message(journal_entry.content)
        return {"message": message}
    except Exception as e:
        logger.error(f"Error generating message: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate message.")

@router.get("/journal/today")
async def get_todays_journal(user_id: int = 1):
    try:
        integration = NotionIntegrationManager().get_integration_by_user_id(user_id)
        if not integration:
            raise HTTPException(status_code=404, detail="Notion integration not found for this user.")
        
        content = NotionManager.get_latest_journal_entry(
            notion_token=integration.access_token,
            database_id=integration.page_id
        )
        if content:
            return {"content": content}
        else:
            return {"content": ""}
    except Exception as e:
        logger.error(f"Error fetching today's journal: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch today's journal.")

@router.post("/send-email/")
async def send_email(email_request: EmailRequest):
    try:
        EmailManager.send_motivational_email(user_id=1, to_email=email_request.to_email, message=email_request.message)
        return {"status": "Email sent"}
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email.")

@router.get("/test-notion-fetch")
async def test_notion_fetch(user_id: int):
    try:
        integration = NotionIntegrationManager().get_integration_by_user_id(user_id)
        content = NotionManager.get_latest_journal_entry(notion_token=integration.access_token, database_id=integration.page_id)
        if content:
            return {"notion_content": content}
        else:
            return {"notion_content": "No content found or error occurred."}
    except Exception as e:
        logger.error(f"Error testing Notion fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Notion data: {e}")

@router.post("/process-and-email-journal")
async def process_and_email_journal():
    try:
        # Hardcoded email for now, as requested
        recipient_email = os.getenv("RECIPIENT_EMAIL") # REPLACE WITH ACTUAL RECIPIENT EMAIL
        result = await JournalManager.process_and_email_latest_journal(recipient_email)
        if result["message"] is None:
            raise HTTPException(status_code=404, detail=result["status"])
        return result
    except Exception as e:
        logger.error(f"Error processing and emailing journal: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process and email journal: {e}")
