from pydantic import BaseModel

class NotionAuthCode(BaseModel):
    code: str

class Token(BaseModel):
    access_token: str
    token_type: str
    existing_user: bool
