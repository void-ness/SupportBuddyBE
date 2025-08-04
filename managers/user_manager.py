from typing import Optional
from datetime import datetime

from models.models import User, UserPydantic
from tortoise.exceptions import DoesNotExist, IntegrityError

class UserManager:
    async def create_user(self, user_data: UserPydantic) -> UserPydantic:
        try:
            user = await User.create(
                username=user_data.username,
                email=user_data.email,
                hashed_password=user_data.hashed_password,
                is_active=user_data.is_active,
                journal_medium=user_data.journal_medium
            )
            return user.to_pydantic()
        except IntegrityError:
            raise Exception("User with this email already exists.")
        except Exception as e:
            raise Exception(f"Database error during user creation: {e}")

    async def get_user_by_email(self, email: str) -> Optional[UserPydantic]:
        try:
            user = await User.filter(email=email).order_by("-created_at").first()
            if user:
                return user.to_pydantic()
            return None
        except Exception as e:
            raise Exception(f"Database error fetching user by email: {e}")

    async def get_or_create_user_by_email(self, email: str) -> (UserPydantic, bool):
        """
        Gets a user by email or creates a new one if they don't exist.
        
        Returns:
            A tuple containing the user object and a boolean (True if created, False if existed).
        """
        user = await self.get_user_by_email(email)
        if user:
            return user, False
        else:
            new_user_data = UserPydantic(
                email=email,
                username=None,
                hashed_password=None,
                is_active=True,
                journal_medium="notion"
            )
            created_user = await self.create_user(new_user_data)
            return created_user, True

    async def get_user_by_id(self, user_id: int) -> Optional[UserPydantic]:
        try:
            user = await User.get_or_none(id=user_id)
            if user:
                return user.to_pydantic()
            return None
        except Exception as e:
            raise Exception(f"Database error fetching user by ID: {e}")

    async def update_user_journal_medium(self, user_id: int, medium: str):
        try:
            user = await User.get(id=user_id)
            user.journal_medium = medium
            await user.save(update_fields=["journal_medium", "updated_at"])
        except DoesNotExist:
            raise Exception(f"User with ID {user_id} not found.")
        except Exception as e:
            raise Exception(f"Database error updating user journal medium: {e}")

    async def get_active_notion_users(self) -> list[User]:
        try:
            users = await User.filter(is_active=True, journal_medium="notion")
            return users
        except Exception as e:
            raise Exception(f"Database error fetching active Notion users: {e}")

    async def deactivate_long_inactive_users(self, inactivity_threshold: int) -> int:
        """
        Deactivates users who have been inactive for a specified number of days using a single update query.
        
        Args:
            inactivity_threshold: The number of days of inactivity to trigger deactivation.
            
        Returns:
            The number of users deactivated.
        """
        try:
            rows_affected = await User.filter(
                is_active=True,
                inactive_days_counter__gte=inactivity_threshold
            ).update(is_active=False, updated_at=datetime.utcnow())
            
            return rows_affected
        except Exception as e:
            raise Exception(f"Database error during user deactivation: {e}")
