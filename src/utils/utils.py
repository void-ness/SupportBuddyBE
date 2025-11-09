import os
from datetime import datetime, timedelta
from typing import Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from cryptography.fernet import Fernet

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Encryption settings
FERNET_KEY = os.getenv("FERNET_KEY")
if FERNET_KEY is None:
    raise ValueError("FERNET_KEY environment variable not set.")
fernet = Fernet(FERNET_KEY)

def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    return fernet.decrypt(encrypted_data.encode()).decode()

def strip_values(data: BaseModel, size_limits: dict) -> BaseModel:
    """
    Strip values in the data model if they exceed the specified size limits.

    :param data: Pydantic model containing the data to be processed.
    :param size_limits: Dictionary containing the size limits for each field.
    :return: Processed data model with values stripped to the size limits.
    """
    for key, limit in size_limits.items():
        value = getattr(data, key, None)
        if value and isinstance(value, str) and len(value) > limit:
            setattr(data, key, value[:limit])
    return data
