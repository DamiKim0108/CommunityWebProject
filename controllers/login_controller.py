from fastapi.responses import JSONResponse
import re

from controllers.signup_controller import find_user_by_email, PWD_REGEX

def login(payload: dict):
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        return JSONResponse(status_code=400, content={
            "message": "invalid_request",
            "data": None
        })

    # 이메일 형식
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return JSONResponse(status_code=422, content={
            "message": "validation_error",
            "data": None
        })

    # 비밀번호 형식
    if not PWD_REGEX.match(password):
        return JSONResponse(status_code=400, content={
            "message": "invalid_request",
            "data": None
        })

    user = find_user_by_email(email)
    if not user or user["password"] != password:
        return JSONResponse(status_code=401, content={
            "message": "unauthorized",
            "data": None
        })

    return JSONResponse(status_code=200, content={
        "message": "login_success",
        "data": {
            "redirect": "/posts"
        }
    })
