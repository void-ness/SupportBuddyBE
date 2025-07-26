from fastapi import APIRouter, BackgroundTasks, HTTPException, status
import logging

from managers.batch_processor import BatchProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

batch_processor = BatchProcessor()

@router.post("/schedule/process-notion-journals")
async def schedule_notion_journal_processing(background_tasks: BackgroundTasks):
    logger.info("Received request to schedule Notion journal processing.")
    background_tasks.add_task(batch_processor.process_notion_users_in_batches)
    return {"message": "Notion journal processing scheduled in background."}
