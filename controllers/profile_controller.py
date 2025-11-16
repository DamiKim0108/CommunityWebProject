from fastapi.responses import JSONResponse

from controllers.signup_controller import find_user_by_email

def edit_profile(payload: dict):
    email = payload.get("email")
    nickname = payload.get("nickname")
    profile_image = payload.get("profile_image")

    if not email or not nickname:
        return JSONResponse(status_code=400, content={
            "message": "invalid_request",
            "data": None
        })

    user = find_user_by_email(email)
    if not user:
        return JSONResponse(status_code=404, content={
            "message": "not_found",
            "data": None
        })

    user["nickname"] = nickname
    user["profile_image"] = profile_image or user.get("profile_image")

    return JSONResponse(status_code=200, content={
        "message": "profile_updated",
        "data": {
            "nickname": user["nickname"],
            "profile_image": user["profile_image"]
        }
    })
