from typing import Optional
from pydantic import BaseModel
from datetime import datetime

#AUTH
class RegisterFormData(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str


class LoginFormData(BaseModel):
    email: str
    password: str

# USER
class User(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    gender: str
    program: str
    level: int
    biography: str

# SESSION MODEL
class Session(BaseModel):
    title: str
    course_code: str
    max_capacity: int
    description: str
    location: str
    meeting_type: str
    date: datetime
    last_updated: datetime
