# controllers/user_controller.py
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from models import user_model


def signup_controller(db: Session, payload: Dict[str, Any]):
    try:
        email = payload.get("email")
        password = payload.get("password")
        nickname = payload.get("nickname")
        profile_image = payload.get("profile_image")

        result = user_model.create_user(db, email, password, nickname, profile_image)
        err = result.get("error")

        if err == "invalid_request":
            return JSONResponse(status_code=400, content={
                "message": "invalid_request",
                "data": None,
            })
        if err == "validation_error":
            return JSONResponse(status_code=422, content={
                "message": "validation_error",
                "data": {"field": result.get("field")},
            })
        if err == "email_conflict":
            return JSONResponse(status_code=409, content={
                "message": "email_conflict",
                "data": None,
            })

        return JSONResponse(status_code=201, content={
            "message": "register_success",
            "data": {"user_id": result["user_id"]},
        })
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None,
        })


def login_controller(db: Session, payload: Dict[str, Any]):
    try:
        email = payload.get("email")
        password = payload.get("password")

        result = user_model.authenticate_user(db, email, password)
        err = result.get("error")

        if err == "invalid_request":
            return JSONResponse(status_code=400, content={
                "message": "invalid_request",
                "data": None,
            })
        if err == "unauthorized":
            return JSONResponse(status_code=401, content={
                "message": "unauthorized",
                "data": None,
            })

        return JSONResponse(status_code=200, content={
            "message": "login_success",
            "data": {"user_id": result["user_id"]},
        })
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None,
        })


def edit_profile_controller(db: Session, payload: Dict[str, Any]):
    try:
        user_id = payload.get("user_id")
        nickname = payload.get("nickname")
        profile_image = payload.get("profile_image")

        result = user_model.update_profile(db, user_id, nickname, profile_image)
        err = result.get("error")

        if err == "not_found":
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None,
            })
        if err == "invalid_request":
            return JSONResponse(status_code=400, content={
                "message": "invalid_request",
                "data": None,
            })
        if err == "nickname_too_long":
            return JSONResponse(status_code=422, content={
                "message": "validation_error",
                "data": {"field": "nickname", "reason": "too_long"},
            })

        return JSONResponse(status_code=200, content={
            "message": "profile_updated",
            "data": result,
        })
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None,
        })


def edit_password_controller(db: Session, payload: Dict[str, Any]):
    try:
        user_id = payload.get("user_id")
        old_password = payload.get("old_password")
        new_password = payload.get("new_password")

        result = user_model.update_password(db, user_id, old_password, new_password)
        err = result.get("error")

        if err == "not_found":
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None,
            })
        if err == "wrong_password":
            return JSONResponse(status_code=401, content={
                "message": "unauthorized",
                "data": None,
            })
        if err == "validation_error":
            return JSONResponse(status_code=422, content={
                "message": "validation_error",
                "data": None,
            })

        return JSONResponse(status_code=200, content={
            "message": "password_updated",
            "data": {"user_id": result["user_id"]},
        })
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None,
        })
