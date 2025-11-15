'''
1. Body(JSON)에서 이메일/비번/닉네임/프로필URL을 뽑는다.
2. 필수값/형식 검증:
    빠진 값 있으면 → 400 + "invalid_request"
    형식 안 맞으면 → 422 + "validation_error"
    이메일 중복이면 → 409 + "email_duplicated"
    닉네임 중복이면 → 409 + "nickname_duplicated"
모두 통과하면:
    새 user_id 생성
    전역 in-memory DB (USERS)에 저장
    201 + "register_success" + user_id 를 응답

예기치 못한 에러 발생:
500 + "internal_server_error" 반환
'''



# routers/signup_router.py
from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import JSONResponse
import re, itertools

router = APIRouter(prefix="/users", tags=["SignUp"])

# -----------------------------
# Mock DB / State (다른 라우터가 import해서 씁니다)
# -----------------------------
_user_id_seq = itertools.count(start=1)
REGISTERED_EMAILS = {"taken@startupcode.kr"}
REGISTERED_NICKNAMES = {"dami", "admin", "tester"}
USERS: dict[str, dict] = {}   # <-- 로그인 라우터가 여기서 조회

# -----------------------------
# Design tokens / helper texts
# -----------------------------
DEFAULT_COLOR = "#ACA0EB"
ACTIVE_COLOR = "#7F6AEE"

HELPER = {
    "email": "올바른 이메일 형식을 입력해주세요. (예: example@example.com)",
    "password": "비밀번호는 8~20자, 대/소문자/숫자/특수문자 각 1개 이상 포함.",
    "nickname": "닉네임은 공백 없이 1~10자, 한글/영문/숫자만 가능.",
    "profile": "프로필 사진을 추가해 주세요."
}

# -----------------------------
# Validators
# -----------------------------
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PWD_RE   = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*]).{8,20}$")
NICK_RE  = re.compile(r"^[가-힣A-Za-z0-9]{1,10}$")

def button_color(valid: bool) -> str:
    return ACTIVE_COLOR if valid else DEFAULT_COLOR

# 필수값 + 형식 검사
# invalid_request : 하나라도 비어있은 경우
# validation_error_email : 이메일 형식 오류
# validation_error_password : 비밀번호 형식 오류
# validation_error_nickname : 닉네임 형식 오류
# True, "ok" : 모두 통과
def validate_signup_fields(email: str | None, password: str | None, nickname: str | None):
    if not email or not password or not nickname:
        return False, "invalid_request"
    if not EMAIL_RE.match(email):
        return False, "validation_error_email"
    if not PWD_RE.match(password):
        return False, "validation_error_password"
    if not NICK_RE.match(nickname):
        return False, "validation_error_nickname"
    return True, "ok"

# -----------------------------
# Meta (helper text, colors)
# -----------------------------
@router.get("/signup/meta")
def signup_meta():
    return JSONResponse(content={
        "message": "meta_ok",
        "data": {"helper_text": HELPER, "colors": {"default": DEFAULT_COLOR, "active": ACTIVE_COLOR}}
    })

# -----------------------------
# 중복 체크
# -----------------------------
@router.post("/signup/check-email")
def check_email(payload: dict):
    email = (payload or {}).get("email")
    if not email:
        return JSONResponse(status_code=400, content={"message": "invalid_request", "data": None})
    if not EMAIL_RE.match(email):
        return JSONResponse(status_code=422, content={"message": "validation_error", "data": None})
    available = (email not in REGISTERED_EMAILS) and (email not in USERS)
    return JSONResponse(content={"message": "available" if available else "duplicated",
                                 "data": {"email": email, "available": available}})

@router.post("/signup/check-nickname")
def check_nickname(payload: dict):
    nickname = (payload or {}).get("nickname")
    if not nickname:
        return JSONResponse(status_code=400, content={"message": "invalid_request", "data": None})
    if not NICK_RE.match(nickname):
        return JSONResponse(status_code=422, content={"message": "validation_error", "data": None})
    available = nickname not in REGISTERED_NICKNAMES and all(u["nickname"] != nickname for u in USERS.values())
    return JSONResponse(content={"message": "available" if available else "duplicated",
                                 "data": {"nickname": nickname, "available": available}})

# -----------------------------
# 프로필 이미지 업로드/삭제 (모의)
# -----------------------------
@router.post("/signup/profile-image")
async def upload_profile_image(file: UploadFile = File(...)):
    preview_url = f"mock://preview/{file.filename}"
    return JSONResponse(status_code=201, content={
        "message": "upload_success",
        "data": {"filename": file.filename, "content_type": file.content_type, "preview_url": preview_url}
    })

@router.delete("/signup/profile-image")
def delete_profile_image(name: str = Query(None, description="삭제할 파일 이름(옵션)")):
    return JSONResponse(content={"message": "delete_success", "data": {"deleted": name or True}})



'''
--------------
회원가입 
--------------
'''
@router.post("/signup")
def signup(payload: dict):
    # body에서 값 꺼내기
    # payload or {} : payload=None이어도 .get()에서 에러 나지 않도록하는 방어코드
    try:
        email    = (payload or {}).get("email")
        password = (payload or {}).get("password")
        nickname = (payload or {}).get("nickname")
        profile_image = (payload or {}).get("profile_image")

        # 필수값, 형식 체크
        # 400 : email/password/nickname 중 하나라도 없을 때
        # 409 : 이메일/닉네임 중복
        # 422 :이메일/비밀번호/닉네임 형식 검증 실패

        ok, key = validate_signup_fields(email, password, nickname)

        # ok=False : key에 따라 상태코드, message 결정
        if not ok:
            return JSONResponse(status_code=422 if key.startswith("validation") else 400,
                                content={"message": "validation_error" if key.startswith("validation") else "invalid_request",
                                         "data": {"button_color": button_color(False)}})
        # 이메일 중복 여부
        # REGISTERED_EMAILS : 이미 사용 중인 이메일 셋
        # USERS : 가입된 유저들을 in-memory로 저장ㅇ하는 dict
        if email in REGISTERED_EMAILS or email in USERS:
            return JSONResponse(status_code=409, content={"message": "email_duplicated",
                                                          "data": {"button_color": button_color(False)}})
        # 닉네임 중복 여부
        # REGISTERED_NICKNAMES : 미리 막아둔 닉네임 목록
        # 가입한 모든 유저를 순회하며 요청 닉네임과 같은게 하나라도 있으면 True
        if nickname in REGISTERED_NICKNAMES or any(u["nickname"] == nickname for u in USERS.values()):
            return JSONResponse(status_code=409, content={"message": "nickname_duplicated",
                                                          "data": {"button_color": button_color(False)}})

        # 가입처리
        user_id = next(_user_id_seq)
        REGISTERED_EMAILS.add(email)
        REGISTERED_NICKNAMES.add(nickname)
        USERS[email] = {   # <-- 로그인 라우터에서 참조
            "user_id": user_id,
            "email": email,
            "password": password,  # 데모용: 해시 없이 저장
            "nickname": nickname,
            "profile_image": profile_image
         }
        # 성공적으로 회원가입
        return JSONResponse(status_code=201, content={
            "message": "register_success",
            "data": {"user_id": user_id, "redirect": "/login", "button_color": button_color(True),
                     "profile_image": profile_image}
        })
    # 예외 처리
    except Exception:
        return JSONResponse(status_code=500, content={"message": "internal_server_error", "data": None})
