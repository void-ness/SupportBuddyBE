from typing import Optional
from fastapi import HTTPException, status
from psycopg2.errors import UniqueViolation

from models.models import User
from managers.user_manager import UserManager
from utils.utils import get_password_hash, create_access_token, verify_password

class AuthManager:
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

    def signup_user(self, username: str, email: str, password: str) -> dict:
        try:
            hashed_password = get_password_hash(password)
            user_data = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                is_active=True,
                journal_medium="web"
            )
            new_user = self.user_manager.create_user(user_data)
            access_token = create_access_token(data={"sub": str(new_user.id)})
            return {"access_token": access_token, "token_type": "bearer"}
        except UniqueViolation:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email or username already exists.")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred during signup: {e}")

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.user_manager.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def create_user_token(self, user: User) -> dict:
        access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
