'''
1. 요청 JSON에서 email, nickname, profile 가져오기
2. 필수값 검증
3.이메일로 사용자 확인
4. 닉네임 형식 확인 / 중복 검사
5. USERS 데이터에 실제 값 반영
6. 닉네임 중복 체크용  set 업데이트
7. 성공 응답 반환

'''



from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
import re

# signup_router에서 사용하는 in-memory DB 재사용
from routers.signup_router import USERS, REGISTERED_EMAILS, REGISTERED_NICKNAMES

router = APIRouter(prefix="/users", tags=["Profile"])

# 닉네임: 한글/영문/숫자, 1~10자
NICK_RE = re.compile(r"^[가-힣A-Za-z0-9]{1,10}$")

HOVER_COLOR = "#E9E9E9"  # 프로필 이미지 hover 시 배경색


# -----------------------------
# 메타 정보 (helper text / 드롭다운 메뉴 / 색상)
# -----------------------------
@router.get("/profile/meta")
def profile_meta():
    try:
        return JSONResponse(content={
            "message": "meta_ok",
            "data": {
                "helper_text": {
                    "nickname_required": "*닉네임을 입력해주세요.",
                    "nickname_duplicated": "*중복된 닉네임 입니다.",
                    "nickname_too_long": "*닉네임은 최대 10자 까지 작성 가능합니다."
                },
                # 프로필 이미지 클릭 시 드롭다운으로 이동할 수 있는 메뉴 예시
                "profile_menu": [
                    {"label": "회원정보 수정", "url": "/users/profile"},
                    {"label": "비밀번호 수정", "url": "/users/passward"},
                    {"label": "로그아웃", "url": "/logout"}
                ],
                "hover_color": HOVER_COLOR
            }
        })
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })


# -----------------------------
# 2. 회원정보 수정 (닉네임 / 프로필 이미지)
# -----------------------------
@router.patch("/profile")
def update_profile(payload: dict | None = Body(None)):
    try:
        email         = (payload or {}).get("email")
        new_nickname  = (payload or {}).get("nickname")
        new_profile   = (payload or {}).get("profile_image")

        # 필수값(email, nickname+) 체크
        if not email or not new_nickname:
            return JSONResponse(status_code=400, content={
                "message": "invalid_request",
                "data": None
            })

        #회원 존재 여부
        user = USERS.get(email)
        if not user:
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None
            })

        # 닉네임 형식 검증 (1~10자, 한글/영문/숫자)
        if not NICK_RE.match(new_nickname):
            return JSONResponse(status_code=422, content={
                "message": "validation_error",
                "data": None
            })
        
        
        old_nickname = user["nickname"]

        # 닉네임 중복 체크 (본인 제외)
        # 본인이 이미 사용하는 닉네임이면 중복 아님
        # 중복 기준
        # -  REGISTERED_NICKNAMES set에 이미 존재
        # - USERS 전체에 동일한 닉네임 가진 사용자 있는 경우
        if new_nickname != old_nickname:
            if (new_nickname in REGISTERED_NICKNAMES or
                    any(u["nickname"] == new_nickname for u in USERS.values())):
                return JSONResponse(status_code=409, content={
                    "message": "nickname_duplicated",
                    "data": None
                })

        # 수정 반영
        user["nickname"] = new_nickname
        if new_profile is not None:
            user["profile_image"] = new_profile

        # 닉네임 set 업데이트
        if new_nickname != old_nickname:
            REGISTERED_NICKNAMES.discard(old_nickname)
            REGISTERED_NICKNAMES.add(new_nickname)

        return JSONResponse(status_code=200, content={
            "message": "update_success",
            "data": {
                "user_id": user["user_id"],
                "nickname": user["nickname"],
                "profile_image": user.get("profile_image")
            }
        })

    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })


# -----------------------------
# 3. 회원 탈퇴
# -----------------------------
@router.delete("/profile")
def delete_profile(payload: dict | None = Body(None)):
    try:
        email = (payload or {}).get("email")
        
        # 이메일로 회원 식별 (필수값)
        if not email:
            return JSONResponse(status_code=400, content={
                "message": "invalid_request",
                "data": None
            })
        
        # 회원 존재 여부 확인
        # USERS : signup으로 생성된 유저 db
        # key = email
        user = USERS.pop(email, None)
        if not user:
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None
            })

        # 중복체크용 set에서도 제거
        REGISTERED_EMAILS.discard(user["email"])
        REGISTERED_NICKNAMES.discard(user["nickname"])

        # 요구사항: 회원 탈퇴 완료 후 로그인 페이지로 이동
        return JSONResponse(status_code=200, content={
            "message": "withdraw_success",
            "data": {
                "redirect": "/login"
            }
        })

    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })
