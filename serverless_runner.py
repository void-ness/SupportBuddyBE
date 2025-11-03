"""
Standalone script to run journal processing tasks.
This can be used for local testing or as a reference for the GitHub Actions workflow.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from managers.batch_processor import BatchProcessor
from utils.database import init_db, close_db_connection_pool
from utils.logging_config import setup_logging


async def run_process_journals():
    """Process Notion journals for active users."""
    print("🚀 Starting Notion journal processing...")
    try:
        processor = BatchProcessor()
        await processor.process_notion_users_in_batches()
        print("✅ Successfully processed Notion journals")
        return True
    except Exception as e:
        print(f"❌ Error processing journals: {e}")
        return False


async def run_deactivate_users():
    """Deactivate inactive users."""
    print("🚀 Starting user deactivation process...")
    try:
        processor = BatchProcessor()
        await processor.process_user_deactivation()
        print("✅ Successfully processed user deactivation")
        return True
    except Exception as e:
        print(f"❌ Error processing user deactivation: {e}")
        return False


async def run_send_reminders():
    """Send reminder emails to recently active users."""
    print("🚀 Starting reminder email process...")
    try:
        processor = BatchProcessor()
        await processor.process_inactive_user_reminders_in_batches()
        print("✅ Successfully sent reminder emails")
        return True
    except Exception as e:
        print(f"❌ Error sending reminders: {e}")
        return False


async def main():
    """Main entry point for the serverless journal processing."""
    
    # Initialize logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("🔧 Serverless runner started - logging initialized")
    
    # Check for required environment variables
    required_vars = [
        'DATABASE_URL',
        'MAILGUN_API_KEY', 
        'MAILGUN_DOMAIN',
        'GOOGLE_GENAI_API_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Get task type from environment or default to all tasks
    task_type = os.getenv('TASK_TYPE', 'all')
    
    logger.info(f"🎯 Running task type: {task_type}")
    print(f"🎯 Running task type: {task_type}")
    
    try:
        # Initialize database connection
        await init_db()
        logger.info("✅ Database connection initialized")
        print("✅ Database connection initialized")
        
        results = []
        
        if task_type in ['process-journals', 'all']:
            results.append(await run_process_journals())
        
        if task_type in ['deactivate-users', 'all']:
            results.append(await run_deactivate_users())
        
        if task_type in ['send-reminders', 'all']:
            results.append(await run_send_reminders())
        
        # Check if all tasks succeeded
        if all(results):
            print("🎉 All tasks completed successfully!")
            return 0
        else:
            print("⚠️  Some tasks failed")
            return 1
            
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        return 1
    finally:
        # Always close database connections
        await close_db_connection_pool()
        print("🔌 Database connections closed")


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)