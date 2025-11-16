from fastapi import UploadFile
from fastapi.responses import JSONResponse

from controllers.makepost_controller import POSTS, MAX_TITLE_LEN

def build_image_info(post: dict):
    filename = post.get("image_filename")
    if not filename:
        return None
    return {
        "filename": filename,
        "url": f"/static/uploads/{filename}"
    }


def get_edit_post_meta(post_id: int):
    post = next((p for p in POSTS if p["id"] == post_id), None)
    if not post:
        return JSONResponse(status_code=404, content={
            "message": "not_found",
            "data": None
        })

    return JSONResponse(content={
        "message": "edit_meta_ok",
        "data": {
            "post": {
                "id": post["id"],
                "title": post["title"],
                "body": post["body"],
                "created_at": post["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                "author": post["author"],
                "image": build_image_info(post)
            },
            "max_title_length": MAX_TITLE_LEN,
            "helper_text": {
                "title_rule": "*제목은 최대 26자까지 작성 가능합니다.",
                "title_required": "*제목을 입력해주세요.",
                "body_required": "*내용을 입력해주세요."
            }
        }
    })


async def update_post(
    post_id: int,
    title: str,
    body: str,
    image: UploadFile | None,
    remove_image: str | None
):
    post = next((p for p in POSTS if p["id"] == post_id), None)
    if not post:
        return JSONResponse(status_code=404, content={
            "message": "not_found",
            "data": None
        })

    title = title.strip()
    body = body.strip()

    if not title or not body:
        return JSONResponse(status_code=400, content={
            "message": "invalid_request",
            "data": None
        })

    if len(title) > MAX_TITLE_LEN:
        return JSONResponse(status_code=422, content={
            "message": "validation_error",
            "data": {"field": "title", "reason": "too_long"}
        })

    if image is not None:
        if not image.content_type.startswith("image/"):
            return JSONResponse(status_code=422, content={
                "message": "validation_error",
                "data": {"field": "image", "reason": "not_image"}
            })
        post["image_filename"] = image.filename
    elif remove_image is not None and remove_image.lower() == "true":
        post["image_filename"] = None

    post["title"] = title
    post["body"] = body

    return JSONResponse(content={
        "message": "post_updated",
        "data": {
            "post_id": post_id,
            "detail_url": f"/posts/{post_id}"
        }
    })
