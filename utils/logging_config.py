import logging
import sys

def setup_logging():
    """
    Configures logging for the application, including SQL query logging.
    """
    # Configure basic logging
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Configure Tortoise ORM query logging
    sql_debug_logger = logging.getLogger("tortoise.db_client")
    sql_debug_logger.setLevel(logging.DEBUG)
    
    # Create a handler that outputs to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    sql_debug_logger.addHandler(console_handler)
    
    # Prevent query logs from propagating to the root logger to avoid duplicates
    sql_debug_logger.propagate = False

    logging.getLogger(__name__).info("Logging configured successfully.")
