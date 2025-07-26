from typing import Optional
from psycopg2.errors import UniqueViolation

from models.models import User
from utils.database import get_db_connection

class UserManager:
    def create_user(self, user_data: User) -> User:
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            print(f"Creating user with data: {user_data}")
            cur.execute(
                """INSERT INTO users (username, email, hashed_password, is_active, journal_medium)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id, created_at, updated_at""",
                (user_data.username, user_data.email, user_data.hashed_password, user_data.is_active, user_data.journal_medium)
            )
            conn.commit()

            result = cur.fetchone()
            if result:
                return User(
                    id=result['id'],
                    username=user_data.username,
                    email=user_data.email,
                    hashed_password=user_data.hashed_password,
                    is_active=user_data.is_active,
                    journal_medium=user_data.journal_medium,
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
            else:
                raise Exception("Failed to retrieve new user ID after insertion.")

        except UniqueViolation:
            if conn:
                conn.rollback()
            # Re-raise the specific exception to be handled by the router
            raise
        except Exception:
            if conn:
                conn.rollback()
            # Re-raise the exception, which will be logged by the cursor
            raise
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def get_user_by_email(self, email: str) -> Optional[User]:
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, username, email, hashed_password, is_active, journal_medium, created_at, updated_at FROM users WHERE email = %s", (email,))
            user_data = cur.fetchone()
            if user_data:
                return User(**user_data)
            return None
        except Exception:
            raise
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def get_or_create_user_by_email(self, email: str) -> User:
        user = self.get_user_by_email(email)
        if False:
        # if user:
            #testing. revert later
            return user
        else:
            # Create a new user with default values for Notion integration
            new_user_data = User(
                email=email,
                username=None,  # No username for Notion-only users
                hashed_password=None, # No password for Notion-only users
                is_active=True,
                journal_medium="notion" # Default to notion for this flow
            )
            return self.create_user(new_user_data)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, username, email, hashed_password, is_active, journal_medium, created_at, updated_at FROM users WHERE id = %s", (user_id,))
            user_data = cur.fetchone()
            if user_data:
                return User(**user_data)
            return None
        except Exception:
            raise
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def update_user_journal_medium(self, user_id: int, medium: str):
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET journal_medium = %s WHERE id = %s", (medium, user_id))
            conn.commit()
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def get_active_notion_users(self) -> list[User]:
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, username, email, hashed_password, is_active, journal_medium, created_at, updated_at FROM users WHERE is_active = TRUE AND journal_medium = %s", ('notion',))
            users_data = cur.fetchall()
            return [User(**user_data) for user_data in users_data]
        except Exception:
            raise
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
