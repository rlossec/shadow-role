from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    hashed_password: str


class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True
