"""
Journal-related custom exceptions.
"""


class JournalDatabaseNotFound(Exception):
    """
    Exception raised when a user's Notion journal database cannot be found.
    
    This typically occurs when:
    - The database has been deleted from Notion
    - The database ID in the integration is invalid
    - The user has revoked access to the database
    - The database has been moved or renamed in a way that breaks the integration
    """
    
    def __init__(self, message: str = None):
        super().__init__(message)
