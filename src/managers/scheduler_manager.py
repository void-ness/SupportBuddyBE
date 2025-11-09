import os
import logging
from fastapi import Header, HTTPException, status

logger = logging.getLogger(__name__)

def verify_token(x_auth_token: str = Header(...)):
    expected_token = os.getenv("SCHEDULER_AUTH_TOKEN")
    if not expected_token:
        logger.error("SCHEDULER_AUTH_TOKEN environment variable not set.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: Authentication token not set."
        )
    if x_auth_token != expected_token:
        logger.warning("Unauthorized access attempt to scheduler endpoint.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token."
        )
    return True
