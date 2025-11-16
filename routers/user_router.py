from fastapi import APIRouter
from fastapi.responses import JSONResponse

from controllers.user_controller import (
    signup_controller,
    login_controller,
    edit_password_controller,
    edit_profile_controller,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signup", responses={
    201: {"description": "회원가입 성공"},
    400: {"description": "잘못된 요청"},
    409: {"description": "이메일 중복"},
    422: {"description": "입력 검증 오류"},
    500: {"description": "서버 오류"},
})
def signup(payload: dict):
    try:
        return signup_controller(payload)
    except Exception:
        return JSONResponse(
        status_code=500,
        content={"message": "internal_server_error", "data": None},
    )


@router.post("/login", responses={
    200: {"description": "로그인 성공"},
    400: {"description": "잘못된 요청"},
    401: {"description": "인증 실패"},
    422: {"description": "입력 검증 오류"},
    500: {"description": "서버 오류"},
})
def login(payload: dict):
    try:
        return login_controller(payload)
    except Exception:
        return JSONResponse(
        status_code=500,
        content={"message": "internal_server_error", "data": None},
    )


@router.patch("/password", responses={
    200: {"description": "비밀번호 수정 성공"},
    400: {"description": "잘못된 요청"},
    401: {"description": "현재 비밀번호 불일치"},
    422: {"description": "검증 오류"},
    500: {"description": "서버 오류"},
})
def edit_password(payload: dict):
    try:
        return edit_password_controller(payload)
    except Exception:
        return JSONResponse(
        status_code=500,
        content={"message": "internal_server_error", "data": None},
    )


@router.patch("/profile", responses={
    200: {"description": "프로필 수정 성공"},
    400: {"description": "잘못된 요청"},
    404: {"description": "유저 없음"},
    500: {"description": "서버 오류"},
})
def edit_profile(payload: dict):
    try:
        return edit_profile_controller(payload)
    except Exception:
        return JSONResponse(
        status_code=500,
        content={"message": "internal_server_error", "data": None},
    )
