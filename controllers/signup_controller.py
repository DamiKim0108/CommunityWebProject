from fastapi.responses import JSONResponse
import re
import itertools

# in-memory user 저장소
USERS = []
USER_ID_SEQ = itertools.count(start=1)

# login 테스트용 기본 유저 한 명 생성
USERS.append({
    "id": next(USER_ID_SEQ),
    "email": "test@startupcode.kr",
    "password": "Test@1234",
    "nickname": "startup",
    "profile_image": "https://image.kr/img.jpg"
})

# 공통 이메일 검색 함수
# 다른 controller에서 import해서 사용
def find_user_by_email(email: str):
    return next((u for u in USERS if u["email"] == email), None)


PWD_REGEX = re.compile(
    r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*]).{8,20}$"
)


def signup(payload: dict):
    email = payload.get("email")
    password = payload.get("password")
    nickname = payload.get("nickname")
    profile_image = payload.get("profile_image")

    # 필수값 체크 (이메일, 비밀번호, 닉네임)
    if not email or not password or not nickname:
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

    # 비밀번호 규칙
    if not PWD_REGEX.match(password):
        return JSONResponse(status_code=400, content={
            "message": "invalid_request",
            "data": None
        })

    # 이메일 중복
    if find_user_by_email(email) is not None:
        return JSONResponse(status_code=409, content={
            "message": "conflict_email",
            "data": {
                "button_color": "#7F6AEE"
            }
        })

    # 신규 유저 생성
    user_id = next(USER_ID_SEQ)
    user = {
        "id": user_id,
        "email": email,
        "password": password,
        "nickname": nickname,
        "profile_image": profile_image or None,
    }
    USERS.append(user)

    return JSONResponse(status_code=201, content={
        "message": "register_success",
        "data": {
            "user_id": user_id,
            "redirect": "/login",
            "button_color": "#7F6AEE",
            "profile_image": user["profile_image"]
        }
    })
