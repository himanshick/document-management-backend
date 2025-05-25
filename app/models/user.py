from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserInDB(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: str
    role: str


class UserRole(str, Enum):
    admin = "admin"
    viewer = "viewer"
    editor = "editor"

class UserCreate(UserBase):
    password: str
    role: UserRole          # add this here!
