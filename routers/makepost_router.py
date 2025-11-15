# routers/makepost_router.py

from fastapi import APIRouter, Form, File, UploadFile
from fastapi.responses import JSONResponse
from datetime import datetime
import itertools # 게시글 ID 자동 증가

# 게시글/댓글/좋아요 : posts_router에서 가져옴
from routers.posts_router import POSTS, COMMENTS, LIKES

router = APIRouter(prefix="/posts", tags=["MakePost"])

# 제목 최대 길이
MAX_TITLE_LEN = 26

# 새 게시글 id 자동 증가 시퀀스
POST_ID_SEQ = itertools.count(start=len(POSTS) + 1)


# make post 페이지 메타 정보
@router.get("/new/meta")
def make_post_meta():
    """
    make post(게시글 추가) 페이지용 메타 정보
    - 제목 최대 26자
    - 버튼 색상(비활성/활성)
    - 헬퍼 텍스트
    """
    try:
        return JSONResponse(content={
            "message": "meta_ok",
            "data": {
                "max_title_length": MAX_TITLE_LEN,
                "colors": {
                    "default": "#ACA0EB",   # 비활성
                    "active": "#7F6AEE"     # 제목 + 본문 입력 시 활성
                },
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


# 게시글 생성
# 이미지 업로드(파일) 때문에 JSON body 불가능
# multipart/form-data 사용
'''
title: 필수(Form-data)
body: 필수(Form-data)
image: 선택(Form-data의 File)
'''

@router.post("")
async def create_post(
    title: str = Form(...),
    body: str = Form(...),
    image: UploadFile | None = File(None)
):
    try:
        # 사용자가 앞뒤에 띄어쓰기만 넣어도 입력했다고 착각하는 문제 방지
        title = title.strip()
        body = body.strip()

        # 필수값 검사 (제목/본문 비어있는 경우)
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

        # 이미지 타입 검사 (파일이 png/jpg/jpeg/webp인지 확인)
        image_filename = None
        if image is not None:
            if not image.content_type.startswith("image/"):
                return JSONResponse(status_code=422, content={
                    "message": "validation_error",
                    "data": {
                        "field": "image",
                        "reason": "not_image"
                    }
                })
            image_filename = image.filename

        # 새 게시글 생성
        new_id = next(POST_ID_SEQ)
        now = datetime.utcnow()

        new_post = {
            "id": new_id,
            "title": title,
            "body": body,           # 실제 DB에선 LONGTEXT 컬럼에 매핑된다고 가정
            "created_at": now,
            "comments_count": 0,
            "views": 0,
            "author": "user1",      # 데모용, 실제론 로그인 유저 사용
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

    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })
