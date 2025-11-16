import re
import itertools
from typing import Optional

# in-memory user 저장소
USERS: list[dict] = []
USER_ID_SEQ = itertools.count(start=1)

# 데모용 기본 유저
USERS.append({
    "id": next(USER_ID_SEQ),
    "email": "test@startupcode.kr",
    "password": "Test@1234",  # 실제 서비스라면 해시
    "nickname": "startup",
    "profile_image": "https://image.kr/img.jpg",
})

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PWD_REGEX = re.compile(
    r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*]).{8,20}$"
)


def find_user_by_email(email: str) -> Optional[dict]:
    return next((u for u in USERS if u["email"] == email), None)


def signup_model(payload: dict) -> dict:
    email = payload.get("email")
    password = payload.get("password")
    nickname = payload.get("nickname")
    profile_image = payload.get("profile_image")

    if not email or not password or not nickname:
        return {"message": "invalid_request", "data": None}

    if not EMAIL_REGEX.match(email):
        return {"message": "validation_error", "data": None}

    if not PWD_REGEX.match(password):
        return {"message": "invalid_request", "data": None}

    if find_user_by_email(email) is not None:
        return {
            "message": "conflict_email",
            "data": {
                "button_color": "#7F6AEE"
            }
        }

    user_id = next(USER_ID_SEQ)
    user = {
        "id": user_id,
        "email": email,
        "password": password,
        "nickname": nickname,
        "profile_image": profile_image or None,
    }
    USERS.append(user)

    return {
        "message": "register_success",
        "data": {
            "user_id": user_id,
            "redirect": "/login",
            "button_color": "#7F6AEE",
            "profile_image": user["profile_image"],
        },
    }


def login_model(payload: dict) -> dict:
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        return {"message": "invalid_request", "data": None}

    if not EMAIL_REGEX.match(email):
        return {"message": "validation_error", "data": None}

    if not PWD_REGEX.match(password):
        return {"message": "invalid_request", "data": None}

    user = find_user_by_email(email)
    if not user or user["password"] != password:
        return {"message": "unauthorized", "data": None}

    return {
        "message": "login_success",
        "data": {
            "redirect": "/posts"
        },
    }


def edit_password_model(payload: dict) -> dict:
    email = payload.get("email")
    current_password = payload.get("current_password")
    new_password = payload.get("new_password")
    confirm_password = payload.get("confirm_password")

    if not email or not current_password or not new_password or not confirm_password:
        return {"message": "invalid_request", "data": None}

    user = find_user_by_email(email)
    if not user or user["password"] != current_password:
        return {"message": "unauthorized", "data": None}

    if new_password != confirm_password:
        return {
            "message": "validation_error",
            "data": {
                "field": "confirm_password",
                "reason": "mismatch",
            },
        }

    if not PWD_REGEX.match(new_password):
        return {
            "message": "validation_error",
            "data": {
                "field": "new_password",
                "reason": "weak_password",
            },
        }

    user["password"] = new_password

    return {
        "message": "password_updated",
        "data": None,
    }


def edit_profile_model(payload: dict) -> dict:
    email = payload.get("email")
    nickname = payload.get("nickname")
    profile_image = payload.get("profile_image")

    if not email or not nickname:
        return {"message": "invalid_request", "data": None}

    user = find_user_by_email(email)
    if not user:
        return {"message": "not_found", "data": None}

    user["nickname"] = nickname
    user["profile_image"] = profile_image or user.get("profile_image")

    return {
        "message": "profile_updated",
        "data": {
            "nickname": user["nickname"],
            "profile_image": user["profile_image"],
        },
    }
