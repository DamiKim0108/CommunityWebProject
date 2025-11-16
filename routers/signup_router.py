from fastapi import APIRouter
from fastapi.responses import JSONResponse

from controllers.signup_controller import signup as signup_service

router = APIRouter(prefix="/users", tags=["SignUp"])

@router.post("/signup", responses={
    201: {"description": "회원가입 성공"},
    400: {"description": "잘못된 요청"},
    409: {"description": "이메일 중복"},
    422: {"description": "입력 검증 오류"},
    500: {"description": "서버 오류"},
})
def signup(payload: dict):
    try:
        return signup_service(payload)
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })
