# controllers/editpassword_controller.py
from fastapi.responses import JSONResponse

from controllers.signup_controller import find_user_by_email, PWD_REGEX

def edit_password(payload: dict):
    email = payload.get("email")
    current_password = payload.get("current_password")
    new_password = payload.get("new_password")
    confirm_password = payload.get("confirm_password")

    if not email or not current_password or not new_password or not confirm_password:
        return JSONResponse(status_code=400, content={
            "message": "invalid_request",
            "data": None
        })

    user = find_user_by_email(email)
    if not user or user["password"] != current_password:
        return JSONResponse(status_code=401, content={
            "message": "unauthorized",
            "data": None
        })

    if new_password != confirm_password:
        return JSONResponse(status_code=422, content={
            "message": "validation_error",
            "data": {
                "field": "confirm_password",
                "reason": "mismatch"
            }
        })

    if not PWD_REGEX.match(new_password):
        return JSONResponse(status_code=422, content={
            "message": "validation_error",
            "data": {
                "field": "new_password",
                "reason": "weak_password"
            }
        })

    user["password"] = new_password

    return JSONResponse(status_code=200, content={
        "message": "password_updated",
        "data": None
    })
