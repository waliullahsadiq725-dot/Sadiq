from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field

class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = "student"
    department: str | None = None

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    department: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class BookOut(BaseModel):
    id: int
    title: str
    author: str | None
    description: str | None
    faculty: str | None
    department: str | None
    category: str | None
    status: str
    rejection_reason: str | None
    original_filename: str
    file_size: int
    uploader_id: int
    uploader_name: str
    created_at: datetime

class ReviewIn(BaseModel):
    status: str
    rejection_reason: str | None = None
