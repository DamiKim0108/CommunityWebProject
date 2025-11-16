# routers/login_router.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from controllers.login_controller import login as login_service

router = APIRouter(prefix="/users", tags=["Login"])

@router.post("/login", responses={
    200: {"description": "로그인 성공"},
    400: {"description": "잘못된 요청"},
    401: {"description": "인증 실패"},
    422: {"description": "입력 검증 오류"},
    500: {"description": "서버 오류"},
})
def login(payload: dict):
    try:
        return login_service(payload)
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })
