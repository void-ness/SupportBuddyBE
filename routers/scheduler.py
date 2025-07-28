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

