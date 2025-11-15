from fastapi import APIRouter, Form, File, UploadFile
from fastapi.responses import JSONResponse

from routers.posts_router import POSTS, COMMENTS, LIKES  # 같은 인메모리 DB 공유

router = APIRouter(prefix="/posts", tags=["EditPost"])

# 제목 최대 26자 제한
MAX_TITLE_LEN = 26

'''
이미지 정보 구성 함수
'''
def build_image_info(post: dict) -> dict | None:
    filename = post.get("image_filename")
    if not filename:
        return None
    return {
        "filename": filename,
        "url": f"/static/uploads/{filename}"  # 데모용 경로
    }



# edit post 페이지 진입용 데이터

@router.get("/{post_id}/edit")
def get_edit_post_meta(post_id: int):
    try:
        # 게시글 id로 찾기
        post = next((p for p in POSTS if p["id"] == post_id), None)
        if not post:
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None
            })

        # json 형태로 구성
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
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })



# 게시글 수정
@router.patch("/{post_id}")
async def update_post(
    post_id: int,
    title: str = Form(...),
    body: str = Form(...),
    image: UploadFile | None = File(None),
    remove_image: str | None = Form(None),
):
    try:
        # 수정할 게시글 조회
        post = next((p for p in POSTS if p["id"] == post_id), None)
        if not post:
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None
            })

        # 필수값(제목/본문) 정리 및 공백 제거
        title = title.strip()
        body = body.strip()

        if not title or not body:
            return JSONResponse(status_code=400, content={
                "message": "invalid_request",
                "data": None
            })

        # 제목 길이 검사
        if len(title) > MAX_TITLE_LEN:
            return JSONResponse(status_code=422, content={
                "message": "validation_error",
                "data": {
                    "field": "title",
                    "reason": "too_long"
                }
            })

        # 이미지 처리
        # 새 이미지 업로드가 있다면 타입 검증 후 교체
        if image is not None:
            if not image.content_type.startswith("image/"):
                return JSONResponse(status_code=422, content={
                    "message": "validation_error",
                    "data": {
                        "field": "image",
                        "reason": "not_image"
                    }
                })
            post["image_filename"] = image.filename

        # remove_image="true", 새 이미지가 없음 -> 기존 이미지 삭제
        elif remove_image is not None and remove_image.lower() == "true":
            post["image_filename"] = None

        # 텍스트 업데이트
        post["title"] = title
        post["body"] = body

        detail_url = f"/posts/{post_id}"

        return JSONResponse(content={
            "message": "post_updated",
            "data": {
                "post_id": post_id,
                "detail_url": detail_url
            }
        })

    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })
