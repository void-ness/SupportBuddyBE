from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from tortoise import fields, models

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

class NotionIntegration(models.Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField(unique=True)
    access_token = fields.TextField()
    page_id = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "notion_integrations"

    def to_pydantic(self) -> "NotionIntegrationPydantic":
        return NotionIntegrationPydantic(
            id=self.id,
            user_id=self.user_id,
            access_token=self.access_token,
            page_id=self.page_id,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

class NotionIntegrationPydantic(BaseModel):
    id: Optional[int] = None
    user_id: int
    access_token: str
    page_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
