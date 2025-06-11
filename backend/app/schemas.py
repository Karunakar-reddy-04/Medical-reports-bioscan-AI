from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str
    role: Optional[str] = "patient"

class Token(BaseModel):
    access_token: str
    token_type: str

class ReportOut(BaseModel):
    filename: str
    analysis: str
    doctor_comment: Optional[str]

    class Config:
        orm_mode = True
