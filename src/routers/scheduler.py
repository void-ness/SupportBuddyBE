from fastapi import APIRouter, BackgroundTasks, Depends
import logging

from managers.batch_processor import BatchProcessor
from managers.scheduler_manager import verify_token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/schedule/process-notion-journals", dependencies=[Depends(verify_token)])
async def schedule_notion_journal_processing(background_tasks: BackgroundTasks):
    logger.info("Received request to schedule Notion journal processing.")
    background_tasks.add_task(BatchProcessor().process_notion_users_in_batches)
    return {"message": "Notion journal processing scheduled in background."}


@router.post("/schedule/deactivate-inactive-users", dependencies=[Depends(verify_token)])
async def schedule_deactivate_inactive_users(background_tasks: BackgroundTasks):
    logger.info("Received request to schedule deactivation of inactive users.")
    background_tasks.add_task(BatchProcessor().process_user_deactivation)
    return {"message": "User deactivation process scheduled in background."}


@router.post("/schedule/send-reminder-emails", dependencies=[Depends(verify_token)])
async def schedule_send_reminder_emails(background_tasks: BackgroundTasks):
    logger.info("Received request to schedule sending reminder emails.")
    background_tasks.add_task(BatchProcessor().process_inactive_user_reminders_in_batches)
    return {"message": "Sending reminder emails scheduled in background."}
