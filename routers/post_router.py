from fastapi import APIRouter, Query, Body, Form, File, UploadFile
from fastapi.responses import JSONResponse

from controllers.post_controller import (
    go_write_controller,
    posts_meta_controller,
    list_posts_controller,
    get_post_detail_controller,
    toggle_like_controller,
    list_comments_controller,
    create_comment_controller,
    update_comment_controller,
    delete_comment_controller,
    makepost_meta_controller,
    create_post_controller,
    editpost_meta_controller,
    update_post_controller,
)

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/new")
def go_write():
    try:
        return go_write_controller()
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "internal_server_error", "data": None},
        )


@router.get("/meta")
def posts_meta():
    try:
        return posts_meta_controller()
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "internal_server_error", "data": None},
        )


@router.get("/new/meta")
def get_makepost_meta():
    try:
        return makepost_meta_controller()
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "internal_server_error", "data": None},
        )


@router.get("")
def list_posts(
    cursor: int = Query(0, ge=0, description="다음 페이지의 시작 인덱스(오프셋)"),
    limit: int = Query(10, ge=1, le=50, description="페이지 크기(1~50)"),
):
    try:
        return list_posts_controller(cursor=cursor, limit=limit)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "internal_server_error", "data": None},
        )


@router.post("")
async def make_post(
    title: str = Form(...),
    body: str = Form(...),
    image: UploadFile | None = File(None),
):
    try:
        image_info = None
        if image is not None:
            image_info = {
                "filename": image.filename,
                "content_type": image.content_type,
            }
        return create_post_controller(title=title, body=body, image_info=image_info)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "internal_server_error", "data": None},
        )


@router.get("/{post_id}")
def get_post_detail(post_id: int):
    try:
        return get_post_detail_controller(post_id=post_id)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "internal_server_error", "data": None},
        )


@router.get("/{post_id}/edit")
def get_edit_post(post_id: int):
    try:
        return editpost_meta_controller(post_id=post_id)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "internal_server_error", "data": None},
        )


@router.patch("/{post_id}")
async def edit_post(
    post_id: int,
    title: str = Form(...),
    body: str = Form(...),
    image: UploadFile | None = File(None),
    remove_image: str | None = Form(None),
):
    try:
        image_info = None
        if image is not None:
            image_info = {
                "filename": image.filename,
                "content_type": image.content_type,
            }
        remove_flag = bool(remove_image and remove_image.lower() == "true")

        return update_post_controller(
            post_id=post_id,
            title=title,
            body=body,
            image_info=image_info,
            remove_image=remove_flag,
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "internal_server_error", "data": None},
        )


@router.post("/{post_id}/like")
def toggle_like(post_id: int, payload: dict | None = Body(None)):
    try:
        return toggle_like_controller(post_id=post_id, payload=payload)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "internal_server_error", "data": None},
        )


@router.get("/{post_id}/comments")
def list_comments(post_id: int):
    try:
        return list_comments_controller(post_id=post_id)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "internal_server_error", "data": None},
        )


@router.post("/{post_id}/comments")
def create_comment(post_id: int, payload: dict | None = Body(None)):
    try:
        return create_comment_controller(post_id=post_id, payload=payload)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "internal_server_error", "data": None},
        )


@router.patch("/{post_id}/comments/{comment_id}")
def update_comment(
    post_id: int,
    comment_id: int,
    payload: dict | None = Body(None),
):

    try:
        return update_comment_controller(
            post_id=post_id,
            comment_id=comment_id,
            payload=payload,
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "internal_server_error", "data": None},
        )


@router.delete("/{post_id}/comments/{comment_id}")
def delete_comment(post_id: int, comment_id: int):
    try:
        return delete_comment_controller(post_id=post_id, comment_id=comment_id)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "internal_server_error", "data": None},
        )
