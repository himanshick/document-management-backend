from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    editor = "editor"
    viewer = "viewer"

class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com", description="User's email address")
    full_name: Optional[str] = Field(None, example="John Doe", description="User's full name")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="User's password")
    role: UserRole = Field(..., description="Role assigned to the user")

class UserInDB(UserBase):
    id: str = Field(..., example="60d21b4667d0d8992e610c85", description="Unique user identifier")
    role: UserRole = Field(..., description="User role")

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., example="bearer", description="Token type")

class TokenData(BaseModel):
    sub: str = Field(..., description="Subject / user ID from token")
    role: UserRole = Field(..., description="Role of the user extracted from token")
