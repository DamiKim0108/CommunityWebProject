# routers/user_router.py
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from database import get_db
from controllers.user_controller import (
    signup_controller,
    login_controller,
    edit_profile_controller,
    edit_password_controller,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signup")
def signup(payload: dict = Body(...), db: Session = Depends(get_db)):
    """
    Body 예시:
    {
      "email": "test@startupcode.kr",
      "password": "test1234",
      "nickname": "dami",
      "profile_image": "https://image.kr/img.jpg"
    }
    """
    return signup_controller(db, payload)


@router.post("/login")
def login(payload: dict = Body(...), db: Session = Depends(get_db)):
    """
    Body 예시:
    {
      "email": "test@startupcode.kr",
      "password": "test1234"
    }
    """
    return login_controller(db, payload)


@router.patch("/profile")
def edit_profile(payload: dict = Body(...), db: Session = Depends(get_db)):
    """
    Body 예시:
    {
      "user_id": 1,
      "nickname": "newName",
      "profile_image": "https://image.kr/new.jpg"
    }
    """
    return edit_profile_controller(db, payload)


@router.patch("/password")
def edit_password(payload: dict = Body(...), db: Session = Depends(get_db)):
    """
    Body 예시:
    {
      "user_id": 1,
      "old_password": "test1234",
      "new_password": "NewPass123!"
    }
    """
    return edit_password_controller(db, payload)
