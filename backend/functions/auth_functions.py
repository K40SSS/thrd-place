from fastapi import HTTPException
from fastapi.responses import JSONResponse
from firebase_admin import auth, firestore_async
import requests

import config
from ..models import LoginFormData, RegisterFormData

db = firestore_async.client()

users_db = db.collection("users")


async def register_with_email_password(model: RegisterFormData):
    try:
        user = auth.get_user_by_email(model.email)
        raise HTTPException(status_code=400, detail="User already exists")
    except auth.UserNotFoundError:
        try:
            user = auth.create_user(email=model.email, password=model.password)
            await users_db.document(user.uid).set(
                {
                    "first_name": model.first_name,
                    "last_name": model.last_name,
                    "role": model.role,
                    "photo_url": model.photo_url,
                    "position": "General Member",
                    "degree": "",
                }
            )
            # Create LoginFormData for login
            login_data = LoginFormData(email=model.email, password=model.password)
            return await login_with_email(login_data)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create user: {str(e)}"
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid email format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


async def login_with_email(model: LoginFormData):
    try:
        response = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={config.env["FIREBASE_WEB_API_KEY"]}",
            json={
                "email": model.email,
                "password": model.password,
                "returnSecureToken": True,
            },
        )
        if response.status_code == 200:
            data = response.json()
            uid = data["localId"]
            user_doc = await users_db.document(uid).get()

            response = JSONResponse(
                content={"data": user_doc.to_dict(), "id_token": data["idToken"]}
            )
            response.set_cookie(
                key="firebase_token",
                value=data["idToken"],
                httponly=True,
                # TODO: make it https when in production
                secure=False,  # Allow HTTP for local development
                samesite="lax",  # Less restrictive for cross-browser compatibility
                max_age=60 * 60 * 24 * 7,  # 7 days
            )
            return response
        else:
            try:
                error_data = response.json()
                error_message = error_data.get("error", {}).get(
                    "message", "Invalid email or password"
                )
            except:
                error_message = "Invalid email or password"
            raise HTTPException(status_code=401, detail=error_message)

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Authentication service unavailable: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
