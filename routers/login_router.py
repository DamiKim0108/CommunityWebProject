# routers/login_router.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import re

# 회원가입 라우터의 in-memory DB를 그대로 참조
from routers.signup_router import USERS

router = APIRouter(prefix="/users", tags=["Auth"])

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@router.post("/login")
def login(payload: dict):
    try:
        email = (payload or {}).get("email")
        password = (payload or {}).get("password")

        # 1) 필수 값 검사
        if not email or not password:
            return JSONResponse(status_code=400, content={"message": "invalid_request", "data": None})

        # 2) 이메일 형식 검사
        if not EMAIL_RE.match(email):
            return JSONResponse(status_code=422, content={"message": "validation_error", "data": None})

        # 3) 사용자 인증
        user = USERS.get(email)
        if not user or user["password"] != password:
            return JSONResponse(status_code=401, content={"message": "unauthorized", "data": None})

        # 4) 성공
        return JSONResponse(status_code=200, content={
            "message": "login_success",
            "data": {"redirect": "/posts", "user_id": user["user_id"], "nickname": user["nickname"]}
        })

    except Exception:
        return JSONResponse(status_code=500, content={"message": "internal_server_error", "data": None})
