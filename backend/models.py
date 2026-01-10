#AUTH
from typing import Optional
from pydantic import BaseModel


class RegisterFormData(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str


class LoginFormData(BaseModel):
    email: str
    password: str
