from fastapi.responses import JSONResponse
from typing import Optional

from models.user_model import (
    signup_model,
    login_model,
    edit_password_model,
    edit_profile_model,
)


def signup_controller(payload: dict):
    body = signup_model(payload)
    msg = body["message"]

    if msg == "invalid_request":
        return JSONResponse(status_code=400, content=body)
    if msg == "validation_error":
        return JSONResponse(status_code=422, content=body)
    if msg == "conflict_email":
        return JSONResponse(status_code=409, content=body)

    # register_success
    return JSONResponse(status_code=201, content=body)


def login_controller(payload: dict):
    body = login_model(payload)
    msg = body["message"]

    if msg == "invalid_request":
        return JSONResponse(status_code=400, content=body)
    if msg == "validation_error":
        return JSONResponse(status_code=422, content=body)
    if msg == "unauthorized":
        return JSONResponse(status_code=401, content=body)

    # login_success
    return JSONResponse(status_code=200, content=body)


def edit_password_controller(payload: dict):
    body = edit_password_model(payload)
    msg = body["message"]

    if msg == "invalid_request":
        return JSONResponse(status_code=400, content=body)
    if msg == "validation_error":
        return JSONResponse(status_code=422, content=body)
    if msg == "unauthorized":
        return JSONResponse(status_code=401, content=body)

    # password_updated
    return JSONResponse(status_code=200, content=body)


def edit_profile_controller(payload: dict):
    body = edit_profile_model(payload)
    msg = body["message"]

    if msg == "invalid_request":
        return JSONResponse(status_code=400, content=body)
    if msg == "not_found":
        return JSONResponse(status_code=404, content=body)

    # profile_updated
    return JSONResponse(status_code=200, content=body)
