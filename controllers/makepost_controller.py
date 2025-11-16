from fastapi import UploadFile
from fastapi.responses import JSONResponse
from datetime import datetime
import itertools

# 게시글 · 댓글 · 좋아
POSTS = []
COMMENTS: dict[int, list[dict]] = {}
LIKES: dict[int, dict] = {}
POST_ID_SEQ = itertools.count(start=1)

MAX_TITLE_LEN = 26


def makepost_meta():
    return JSONResponse(content={
        "message": "meta_ok",
        "data": {
            "max_title_length": MAX_TITLE_LEN,
            "colors": {
                "default": "#ACA0EB",
                "active": "#7F6AEE"
            },
            "helper_text": {
                "title_rule": "*제목은 최대 26자까지 작성 가능합니다.",
                "title_required": "*제목을 입력해주세요.",
                "body_required": "*내용을 입력해주세요."
            }
        }
    })


async def create_post(title: str, body: str, image: UploadFile | None):
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

    image_filename = None
    if image is not None:
        if not image.content_type.startswith("image/"):
            return JSONResponse(status_code=422, content={
                "message": "validation_error",
                "data": {"field": "image", "reason": "not_image"}
            })
        image_filename = image.filename

    new_id = next(POST_ID_SEQ)
    now = datetime.utcnow()

    new_post = {
        "id": new_id,
        "title": title,
        "body": body,
        "created_at": now,
        "comments_count": 0,
        "views": 0,
        "author": "user1",
        "image_filename": image_filename,
    }

    POSTS.append(new_post)
    COMMENTS[new_id] = []
    LIKES[new_id] = {"count": 0, "users": set()}

    detail_url = f"/posts/{new_id}"

    return JSONResponse(status_code=201, content={
        "message": "post_created",
        "data": {
            "post_id": new_id,
            "detail_url": detail_url,
            "button_color": "#7F6AEE"
        }
    })
