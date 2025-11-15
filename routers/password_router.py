'''
1. Body에서 email, new_password, new_password_confirm 추출
2. 검사
    - 400 : 셋 중 하나라도 없는 경우
    - 404 : USERS에 해당 이메일 유저 없음
    - 422 : 새 비밀번호가 규칙에 맞지 않음 / 새 비밀번호!=확인값
5. 모든 검증 통과 -> USER의 비밀번호 갱신
'''

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
import re

# 회원 정보를 저장하고 있는 in-memory DB 재사용
from routers.signup_router import USERS

router = APIRouter(prefix="/users", tags=["Password"])

# 비밀번호 정규식: 8~20자, 대/소문자/숫자/특수문자 각각 1개 이상
PWD_RE = re.compile(
    r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*]).{8,20}$"
)

DEFAULT_COLOR = "#ACA0EB"
ACTIVE_COLOR = "#7F6AEE"


# edit password 화면 메타 정보
# front가 페이지 띄울때 필요한 텍스트, 색상 제공
@router.get("/password/meta")
def password_meta():
    try:
        return JSONResponse(content={
            "message": "meta_ok",
            "data": {
                "helper_text": {
                    "rule": "*비밀번호는 8자 이상, 20자 이하이며, 대문자, 소문자, 숫자, 특수문자를 각각 최소 1개 포함해야 합니다.",
                    "password_required": "*비밀번호를 입력해주세요.",
                    "password_confirm_required": "*비밀번호를 한번 더 입력해주세요.",
                    "password_mismatch": "*비밀번호와 다릅니다."
                },
                "colors": {
                    "default": DEFAULT_COLOR,   # ACA0EB
                    "active": ACTIVE_COLOR      # 7F6AEE (모든 입력/검증 통과 시)
                }
            }
        })
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })



# 비밀번호 수정
# | None= Body(None) : body가 비어있어도 함수 호출, payload=None이 됨
@router.patch("/password")
def update_password(payload: dict | None = Body(None)):
    # 요청 body 받기

    try:
        email        = (payload or {}).get("email")
        new_pwd      = (payload or {}).get("new_password")
        new_pwd_conf = (payload or {}).get("new_password_confirm")

        # 필수값 체크
        if not email or not new_pwd or not new_pwd_conf:
            return JSONResponse(status_code=400, content={
                "message": "invalid_request",
                "data": None
            })

        # 사용자 존재 여부
        user = USERS.get(email)
        if not user:
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None
            })

        # 비밀번호 유효성 검사
        if not PWD_RE.match(new_pwd):
            return JSONResponse(status_code=422, content={
                "message": "validation_error",
                "data": None
            })

        # 비밀번호 확인 일치 여부
        if new_pwd != new_pwd_conf:
            return JSONResponse(status_code=422, content={
                "message": "validation_error",
                "data": None
            })

        # 비밀번호 변경
        user["password"] = new_pwd

        # 성공 응답
        return JSONResponse(status_code=200, content={
            "message": "update_success",
            "data": {
                "user_id": user["user_id"]
            }
        })

    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })
