import os
import asyncpg
from dotenv import load_dotenv
import logging

# Set up a specific logger for database queries
db_logger = logging.getLogger("db_queries")
db_logger.setLevel(logging.INFO)

load_dotenv()

# Global connection pool
_pool = None

async def get_db_connection():
    """
    Establishes and returns an asynchronous database connection from the pool.
    """
    global _pool
    if _pool is None:
        db_connection_type = os.getenv("DB_CONNECTION_TYPE", "local") # Default to local
        
        if db_connection_type == "neon":
            connection_string = os.getenv('DATABASE_URL')
            if not connection_string:
                raise ValueError("DATABASE_URL environment variable is not set for NeonDB connection.")
            db_logger.info("Creating NeonDB connection pool...")
            _pool = await asyncpg.create_pool(connection_string)
        
        elif db_connection_type == "local":
            db_logger.info("Creating local PostgreSQL connection pool...")
            _pool = await asyncpg.create_pool(
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
        else:
            raise ValueError(f"Invalid DB_CONNECTION_TYPE: {db_connection_type}. Choose 'neon' or 'local'.")
    
    return await _pool.acquire()

async def close_db_connection_pool():
    """
    Closes the global database connection pool.
    """
    global _pool
    if _pool:
        db_logger.info("Closing database connection pool...")
        await _pool.close()
        _pool = None

