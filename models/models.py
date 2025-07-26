from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class JournalEntry(BaseModel):
    content: str
    user_id: Optional[UUID] = None

class Journal(BaseModel):
    id: str
    user_id: str
    content: str
    created_at: datetime

class Message(BaseModel):
    id: UUID
    user_id: UUID
    journal_entry_id: UUID
    message: str
    sent_at: datetime

class User(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    email: str
    hashed_password: Optional[str] = None
    is_active: bool = True
    journal_medium: str = "web"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class NotionIntegration(BaseModel):
    id: Optional[int] = None
    user_id: int
    access_token: str
    page_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
