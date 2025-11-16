from fastapi import APIRouter
from fastapi.responses import JSONResponse

from controllers.password_controller import edit_password as edit_password_service

router = APIRouter(prefix="/users", tags=["Password"])

@router.patch("/password", responses={
    200: {"description": "비밀번호 수정 성공"},
    400: {"description": "잘못된 요청"},
    401: {"description": "현재 비밀번호 불일치"},
    422: {"description": "검증 오류"},
    500: {"description": "서버 오류"},
})
def edit_password(payload: dict):
    try:
        return edit_password_service(payload)
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })
