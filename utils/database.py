import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

import os
import logging
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Set up a specific logger for database queries
db_logger = logging.getLogger("db_queries")
db_logger.setLevel(logging.INFO)

# --- Custom Cursor for Logging ---
class LoggingCursor(RealDictCursor):
    def execute(self, sql, args=None):
        db_logger.info(f"Executing query: {self.mogrify(sql, args).decode('utf-8')}")
        try:
            super().execute(sql, args)
        except psycopg2.Error as e:
            db_logger.error(f"Database Error: {e.pgcode} - {e.pgerror}")
            raise # Re-raise the exception after logging

    def callproc(self, procname, args=None):
        db_logger.info(f"Calling procedure: {procname} with args: {args}")
        try:
            super().callproc(procname, args)
        except psycopg2.Error as e:
            db_logger.error(f"Database Error on procedure {procname}: {e.pgcode} - {e.pgerror}")
            raise

load_dotenv()

# --- Database Connection ---
def get_db_connection():
    db_connection_type = os.getenv("DB_CONNECTION_TYPE", "local") # Default to local

    try:
        if db_connection_type == "neon":
            connection_string = os.getenv('DATABASE_URL')
            if not connection_string:
                raise ValueError("DATABASE_URL environment variable is not set for NeonDB connection.")
            db_logger.info("Connecting to NeonDB...")
            return psycopg2.connect(connection_string, cursor_factory=LoggingCursor)
        
        elif db_connection_type == "local":
            db_logger.info("Connecting to local PostgreSQL...")
            return psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                cursor_factory=LoggingCursor
            )
        else:
            raise ValueError(f"Invalid DB_CONNECTION_TYPE: {db_connection_type}. Choose 'neon' or 'local'.")
    except psycopg2.Error as e:
        db_logger.error(f"DATABASE CONNECTION FAILED: {e}")
        raise

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            company VARCHAR(255),
            designation VARCHAR(255),
            current_ctc FLOAT,
            total_yoe FLOAT,
            designation_yoe FLOAT,
            performance_rating VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            company VARCHAR(255),
            designation VARCHAR(255),
            current_ctc FLOAT,
            total_yoe FLOAT,
            designation_yoe FLOAT,
            performance_rating VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()
