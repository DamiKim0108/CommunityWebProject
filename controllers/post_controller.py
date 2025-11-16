from fastapi.responses import JSONResponse
from typing import Optional

from models.post_model import (
    go_write_model,
    posts_meta_model,
    list_posts_model,
    get_post_detail_model,
    toggle_like_model,
    list_comments_model,
    create_comment_model,
    update_comment_model,
    delete_comment_model,
    makepost_meta_model,
    create_post_model,
    editpost_meta_model,
    update_post_model,
)


def go_write_controller():
    body = go_write_model()
    return JSONResponse(status_code=200, content=body)


def posts_meta_controller():
    body = posts_meta_model()
    return JSONResponse(status_code=200, content=body)


def list_posts_controller(cursor: int, limit: int):
    body = list_posts_model(cursor, limit)
    return JSONResponse(status_code=200, content=body)


def get_post_detail_controller(post_id: int):
    body = get_post_detail_model(post_id)
    if body["message"] == "not_found":
        return JSONResponse(status_code=404, content=body)
    return JSONResponse(status_code=200, content=body)


def toggle_like_controller(post_id: int, payload: Optional[dict]):
    body = toggle_like_model(post_id, payload)
    msg = body["message"]

    if msg == "invalid_request":
        return JSONResponse(status_code=400, content=body)
    if msg == "not_found":
        return JSONResponse(status_code=404, content=body)

    return JSONResponse(status_code=200, content=body)


def list_comments_controller(post_id: int):
    body = list_comments_model(post_id)
    if body["message"] == "not_found":
        return JSONResponse(status_code=404, content=body)
    return JSONResponse(status_code=200, content=body)


def create_comment_controller(post_id: int, payload: Optional[dict]):
    body = create_comment_model(post_id, payload)
    msg = body["message"]

    if msg == "invalid_request":
        return JSONResponse(status_code=400, content=body)
    if msg == "validation_error":
        return JSONResponse(status_code=422, content=body)
    if msg == "not_found":
        return JSONResponse(status_code=404, content=body)

    return JSONResponse(status_code=201, content=body)


def update_comment_controller(post_id: int, comment_id: int, payload: Optional[dict]):
    body = update_comment_model(post_id, comment_id, payload)
    msg = body["message"]

    if msg == "invalid_request":
        return JSONResponse(status_code=400, content=body)
    if msg == "validation_error":
        return JSONResponse(status_code=422, content=body)
    if msg == "not_found":
        return JSONResponse(status_code=404, content=body)

    return JSONResponse(status_code=200, content=body)


def delete_comment_controller(post_id: int, comment_id: int):
    body = delete_comment_model(post_id, comment_id)
    if body["message"] == "not_found":
        return JSONResponse(status_code=404, content=body)
    return JSONResponse(status_code=200, content=body)


def makepost_meta_controller():
    body = makepost_meta_model()
    return JSONResponse(status_code=200, content=body)


def create_post_controller(title: str, body: str, image_info: Optional[dict]):
    body_dict = create_post_model(title, body, image_info)
    msg = body_dict["message"]

    if msg == "invalid_request":
        return JSONResponse(status_code=400, content=body_dict)
    if msg == "validation_error":
        return JSONResponse(status_code=422, content=body_dict)

    return JSONResponse(status_code=201, content=body_dict)


def editpost_meta_controller(post_id: int):
    body = editpost_meta_model(post_id)
    if body["message"] == "not_found":
        return JSONResponse(status_code=404, content=body)
    return JSONResponse(status_code=200, content=body)


def update_post_controller(
    post_id: int,
    title: str,
    body: str,
    image_info: Optional[dict],
    remove_image: bool,
):
    body_dict = update_post_model(post_id, title, body, image_info, remove_image)
    msg = body_dict["message"]

    if msg == "not_found":
        return JSONResponse(status_code=404, content=body_dict)
    if msg == "invalid_request":
        return JSONResponse(status_code=400, content=body_dict)
    if msg == "validation_error":
        return JSONResponse(status_code=422, content=body_dict)

    return JSONResponse(status_code=200, content=body_dict)
