from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import os


import functions.auth_functions as auth_service
from ..models import LoginFormData, RegisterFormData
import config

router = APIRouter(prefix="/auth") #TODO

@router.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
   
):


    # Create register data
    register_data = RegisterFormData(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        
    )

    return await auth_service.register_with_email_password(register_data)


@router.post("/login")
async def login(model: LoginFormData):
    return await auth_service.login_with_email(model)


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("firebase_token")
    return response
