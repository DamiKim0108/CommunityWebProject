# controllers/post_controller.py
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from models import post_model


def list_posts_controller(db: Session, cursor: int, limit: int):
    try:
        data = post_model.get_post_list(db, cursor, limit)
        return JSONResponse(status_code=200, content={
            "message": "list_ok",
            "data": data,
        })
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None,
        })


def get_post_detail_controller(db: Session, post_id: int):
    try:
        detail = post_model.get_post_detail(db, post_id)
        if not detail:
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None,
            })
        return JSONResponse(status_code=200, content={
            "message": "detail_ok",
            "data": detail,
        })
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None,
        })


def create_post_controller(
    db: Session,
    author_id: int,
    payload: Dict[str, Any],
):
    try:
        title = payload.get("title")
        body = payload.get("body")

        result = post_model.create_post(db, author_id, title, body)
        err = result.get("error")

        if err == "invalid_request":
            return JSONResponse(status_code=400, content={
                "message": "invalid_request",
                "data": None,
            })
        if err == "validation_error":
            return JSONResponse(status_code=422, content={
                "message": "validation_error",
                "data": {"field": result.get("field"), "reason": result.get("reason")},
            })
        if err == "user_not_found":
            return JSONResponse(status_code=404, content={
                "message": "user_not_found",
                "data": None,
            })
        if err == "ai_error":
            return JSONResponse(status_code=502, content={
                "message": "ai_error",
                "data": {"reason": "ai_inference_failed", "error": result.get("detail")},
            })
        if err == "blocked_toxic_post":
            return JSONResponse(status_code=403, content={
                "message": "blocked_toxic_post",
                "data": {
                    "reason": "toxic_content",
                    "model_label": result.get("model_label"),
                    "score": result.get("score"),
                },
            })

        return JSONResponse(status_code=201, content={
            "message": "post_created",
            "data": result,
        })
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None,
        })


def create_comment_controller(
    db: Session,
    post_id: int,
    payload: Optional[Dict[str, Any]],
):
    try:
        author_id = payload.get("author_id")
        content = payload.get("content")

        result = post_model.create_comment(db, post_id, author_id, content)
        err = result.get("error")

        if err == "invalid_request":
            return JSONResponse(status_code=400, content={
                "message": "invalid_request",
                "data": None,
            })
        if err == "validation_error":
            return JSONResponse(status_code=422, content={
                "message": "validation_error",
                "data": None,
            })
        if err == "not_found":
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None,
            })
        if err == "user_not_found":
            return JSONResponse(status_code=404, content={
                "message": "user_not_found",
                "data": None,
            })
        if err == "ai_error":
            return JSONResponse(status_code=502, content={
                "message": "ai_error",
                "data": {"reason": "ai_inference_failed", "error": result.get("detail")},
            })
        if err == "blocked_toxic_comment":
            return JSONResponse(status_code=403, content={
                "message": "blocked_toxic_comment",
                "data": {
                    "reason": "toxic_content",
                    "model_label": result.get("model_label"),
                    "score": result.get("score"),
                },
            })

        return JSONResponse(status_code=201, content={
            "message": "comment_created",
            "data": result,
        })
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None,
        })
