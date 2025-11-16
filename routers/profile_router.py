from fastapi import APIRouter
from fastapi.responses import JSONResponse

from controllers.profile_controller import edit_profile as edit_profile_service

router = APIRouter(prefix="/users", tags=["Profile"])

@router.patch("/profile", responses={
    200: {"description": "프로필 수정 성공"},
    400: {"description": "잘못된 요청"},
    404: {"description": "유저 없음"},
    500: {"description": "서버 오류"},
})
def edit_profile(payload: dict):
    try:
        return edit_profile_service(payload)
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })
