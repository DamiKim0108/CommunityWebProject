# models/user_model.py
from typing import Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db_models import User


def create_user(
    db: Session,
    email: str,
    password: str,
    nickname: str,
    profile_image: Optional[str] = None,
) -> Dict[str, Any]:
    email = (email or "").strip()
    password = (password or "").strip()
    nickname = (nickname or "").strip()

    if not email or not password or not nickname:
        return {"error": "invalid_request"}

    # 아주 간단한 이메일 형식 체크 (정규식 대신)
    if "@" not in email or "." not in email:
        return {"error": "validation_error", "field": "email"}

    new_user = User(
        email=email,
        password=password,  # 실제로는 해시 필요
        nickname=nickname,
        profile_image=profile_image,
        created_at=datetime.utcnow(),
    )

    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # 이메일 unique 제약 위반
        return {"error": "email_conflict"}

    db.refresh(new_user)

    return {"user_id": new_user.id}


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> Dict[str, Any]:
    email = (email or "").strip()
    password = (password or "").strip()

    if not email or not password:
        return {"error": "invalid_request"}

    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"error": "unauthorized"}

    # 데모용: 평문 비교 (실서비스면 비밀번호 해시 비교)
    if user.password != password:
        return {"error": "unauthorized"}

    return {"user_id": user.id}


def update_profile(
    db: Session,
    user_id: int,
    nickname: Optional[str],
    profile_image: Optional[str],
) -> Dict[str, Any]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "not_found"}

    if nickname:
        nickname = nickname.strip()
        if len(nickname) == 0:
            return {"error": "invalid_request"}
        if len(nickname) > 10:
            return {"error": "nickname_too_long"}
        user.nickname = nickname

    if profile_image is not None:
        user.profile_image = profile_image

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "user_id": user.id,
        "nickname": user.nickname,
        "profile_image": user.profile_image,
    }


def update_password(
    db: Session,
    user_id: int,
    old_password: str,
    new_password: str,
) -> Dict[str, Any]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "not_found"}

    if user.password != (old_password or "").strip():
        return {"error": "wrong_password"}

    new_password = (new_password or "").strip()

    if len(new_password) < 8 or len(new_password) > 20:
        return {"error": "validation_error"}

    user.password = new_password
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"user_id": user.id}
