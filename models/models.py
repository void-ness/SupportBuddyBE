from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from tortoise import fields, models

class NotionJournalEntry(BaseModel):
    entry_title: Optional[str] = Field(None, description="The title of the journal entry.")
    gratitude: Optional[str] = Field(None, description="Things the user is grateful for.")
    highlights: Optional[str] = Field(None, description="The highlights of the user's day.")
    challenges: Optional[str] = Field(None, description="Challenges the user faced.")
    reflection: Optional[str] = Field(None, description="The user's reflections on the day.")

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

class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, null=True)
    email = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=255, null=True)
    is_active = fields.BooleanField(default=True)
    inactive_days_counter = fields.IntField(default=0)
    journal_medium = fields.CharField(max_length=50, default="web")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

    def to_pydantic(self) -> "UserPydantic":
        return UserPydantic(
            id=self.id,
            username=self.username,
            email=self.email,
            hashed_password=self.hashed_password,
            is_active=self.is_active,
            inactive_days_counter=self.inactive_days_counter,
            journal_medium=self.journal_medium,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

class UserPydantic(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    email: str
    hashed_password: Optional[str] = None
    is_active: bool = True
    inactive_days_counter: int = 0
    journal_medium: str = "web"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class NotionIntegration(models.Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField(unique=True)
    access_token = fields.TextField()
    page_id = fields.TextField()
    version = fields.TextField(default="v1")
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
            version=self.version,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

class NotionIntegrationPydantic(BaseModel):
    id: Optional[int] = None
    user_id: int
    access_token: str
    page_id: str
    version: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
