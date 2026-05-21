from datetime import datetime

from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    email: str
    password: str = Field(min_length=6)
    name: str = ""


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime
