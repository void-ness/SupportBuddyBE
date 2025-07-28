import os
from dotenv import load_dotenv
import logging
from tortoise import init, close_connections

# Set up a specific logger for database queries
db_logger = logging.getLogger("db_queries")
db_logger.setLevel(logging.INFO)

load_dotenv()

async def init_db():
    db_connection_type = os.getenv("DB_CONNECTION_TYPE", "local")
    if db_connection_type == "neon":
        connection_string = os.getenv('DATABASE_URL')
        if not connection_string:
            raise ValueError("DATABASE_URL environment variable is not set for NeonDB connection.")
        db_logger.info("Initializing Tortoise ORM with NeonDB...")
        await init(db_url=connection_string, modules={"models": ["models.models"]})
    elif db_connection_type == "local":
        db_logger.info("Initializing Tortoise ORM with local PostgreSQL...")
        await init(
            db_url=f"postgres://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
            modules={"models": ["models.models"]}
        )
    else:
        raise ValueError(f"Invalid DB_CONNECTION_TYPE: {db_connection_type}. Choose 'neon' or 'local'.")

async def close_db_connection_pool():
    db_logger.info("Closing Tortoise ORM connections...")
    await close_connections()

