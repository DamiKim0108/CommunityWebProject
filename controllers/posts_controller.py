# controllers/posts_controller.py

from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import itertools

''' -----------------------------
# Mock Data
# 임시 게시글 생성
id, 제목, 생성시간, 댓글, 조회수, 작성자 
i에 따라 시각을 7분씩 증가시켜 게시글 작성 시간 다르게 만듦
 -----------------------------'''
def seed_posts(n: int = 120):
    base = datetime(2023, 11, 3, 12, 0, 0)
    posts = []
    for i in range(1, n + 1):
        posts.append({
            "id": i,
            "title": f"게시글 제목 {i} - 이것은 데모용 긴 제목입니다 (테스트 {i})",
            "body": f"게시글 {i}의 상세 내용입니다. (상세 페이지용 더미 텍스트)",
            "created_at": base + timedelta(minutes=i * 7),
            "comments_count": 0,
            "views": i * 157,      # 임의 값
            "author": f"user{i%7 or 7}",
            "image_filename": None,
        })
    return posts


POSTS = seed_posts()

# post_id -> list[comment_dict]
COMMENTS: dict[int, list[dict]] = {p["id"]: [] for p in POSTS}

# post_id -> {"count": int, "users": set[int]}  (likes per post)
LIKES: dict[int, dict] = {
    p["id"]: {"count": 0, "users": set()} for p in POSTS
}

COMMENT_ID_SEQ = itertools.count(start=1)
POST_ID_SEQ = itertools.count(start=len(POSTS) + 1)

# UI용 메타데이터
# 목록 카드 색상 (hover)
DEFAULT_CARD_COLOR = "#ACA0EB"
HOVER_CARD_COLOR = "#7F6AEE"

# 좋아요 버튼 색상
LIKE_DEFAULT_COLOR = "#D9D9D9"  # disable 색
LIKE_ACTIVE_COLOR = "#ACA0EB"   # enable 색


# 제목이 26자 이상이면 자르기
def truncate_title(title: str, max_len: int = 26) -> str:
    return title if len(title) <= max_len else title[:max_len]

# 작성일 : yyyy-mm-dd hh:mm:ss
def fmt_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# 숫자 압축
def compact_count(n: int) -> str:
    """
    - 1,000 이상  -> 1k
    - 10,000 이상 -> 10k
    - 100,000 이상 -> 100k
    """
    if n >= 100_000:
        return "100k"
    if n >= 10_000:
        return "10k"
    if n >= 1_000:
        return "1k"
    return str(n)


# 목록 카드용 데이터로 가공
def shape_card(post: dict) -> dict:
    return {
        "id": post["id"],
        "title": truncate_title(post["title"], 26),
        "created_at": fmt_datetime(post["created_at"]),
        "comments": compact_count(post["comments_count"]),
        "views": compact_count(post["views"]),
        "detail_url": f"/posts/{post['id']}",
        "colors": {"default": DEFAULT_CARD_COLOR, "hover": HOVER_CARD_COLOR},
    }


# -----------------------------
# Controller functions
# -----------------------------

def go_write():
    """
    GET /posts/new
    새 게시글 작성 페이지 URL 반환
    """
    return JSONResponse(content={
        "message": "go_write",
        "data": {"write_url": "/posts/new"}
    })


def posts_meta():
    """
    GET /posts/meta
    색상 정보, 작성 페이지 URL 등 UI용 데이터 제공
    """
    return JSONResponse(content={
        "message": "meta_ok",
        "data": {
            "colors": {"default": DEFAULT_CARD_COLOR, "hover": HOVER_CARD_COLOR},
            "write_url": "/posts/new"
        }
    })


def list_posts(cursor: int, limit: int):
    """
    게시글 목록 조회 (무한 스크롤)
    - cursor : 다음 페이지를 위한 시작 위치 (offset 기반)
    - limit  : 한번에 가져올 개수 (1~50)
    """
    try:
        total = len(POSTS)
        end = min(cursor + limit, total)
        items = [shape_card(p) for p in POSTS[cursor:end]]
        next_cursor = end if end < total else None

        return JSONResponse(content={
            "message": "list_ok",
            "data": {
                "items": items,
                "next_cursor": next_cursor,
                "total": total
            }
        })
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })


def get_post_detail(post_id: int):
    """
    상세 조회
    - 조회수 1 증가
    - 댓글 목록, 좋아요 수, 조회수/댓글수 표기용 문자열 함께 반환
    """
    try:
        post = next((p for p in POSTS if p["id"] == post_id), None)
        if not post:
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None
            })

        # 조회수 +1
        post["views"] += 1

        comments = COMMENTS.get(post_id, [])
        likes_info = LIKES.get(post_id, {"count": 0, "users": set()})

        return JSONResponse(content={
            "message": "detail_ok",
            "data": {
                "id": post["id"],
                "title": post["title"],
                "body": post["body"],
                "author": post["author"],
                "created_at": fmt_datetime(post["created_at"]),
                "views": post["views"],
                "views_display": compact_count(post["views"]),
                "comments_count": len(comments),
                "comments_count_display": compact_count(len(comments)),
                "likes": likes_info["count"],
                "comments": [
                    {
                        "comment_id": c["id"],
                        "author": c["author"],
                        "content": c["content"],
                        "created_at": fmt_datetime(c["created_at"])
                    }
                    for c in comments
                ]
            }
        })
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })


def toggle_like(post_id: int, payload: dict | None):
    """
    POST /posts/{post_id}/like
    좋아요 토글
    - user_id 필수
    """
    try:
        user_id = (payload or {}).get("user_id")
        if user_id is None:
            return JSONResponse(status_code=400, content={
                "message": "invalid_request",
                "data": None
            })

        post = next((p for p in POSTS if p["id"] == post_id), None)
        if not post:
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None
            })

        like_info = LIKES.setdefault(post_id, {"count": 0, "users": set()})
        users = like_info["users"]

        if user_id in users:
            # 이미 좋아요 → 취소
            users.remove(user_id)
            like_info["count"] = max(0, like_info["count"] - 1)
            liked = False
        else:
            # 처음 좋아요
            users.add(user_id)
            like_info["count"] += 1
            liked = True

        return JSONResponse(content={
            "message": "like_toggled",
            "data": {
                "liked": liked,
                "likes": like_info["count"],
                "button_color": LIKE_ACTIVE_COLOR if liked else LIKE_DEFAULT_COLOR
            }
        })

    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })


def list_comments(post_id: int):
    """
    GET /posts/{post_id}/comments
    댓글 목록 조회
    """
    try:
        post = next((p for p in POSTS if p["id"] == post_id), None)
        if not post:
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None
            })

        comments = COMMENTS.get(post_id, [])

        return JSONResponse(content={
            "message": "comments_ok",
            "data": {
                "comments_count": len(comments),
                "comments_count_display": compact_count(len(comments)),
                "items": [
                    {
                        "comment_id": c["id"],
                        "author": c["author"],
                        "content": c["content"],
                        "created_at": fmt_datetime(c["created_at"])
                    }
                    for c in comments
                ]
            }
        })
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })


def create_comment(post_id: int, payload: dict | None):
    """
    POST /posts/{post_id}/comments
    댓글 등록
    """
    try:
        author = (payload or {}).get("author", "anonymous")
        content = (payload or {}).get("content")

        if not content:
            return JSONResponse(status_code=400, content={
                "message": "invalid_request",
                "data": None
            })

        if len(content) > 500:
            return JSONResponse(status_code=422, content={
                "message": "validation_error",
                "data": None
            })

        post = next((p for p in POSTS if p["id"] == post_id), None)
        if not post:
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None
            })

        comment_id = next(COMMENT_ID_SEQ)
        comment = {
            "id": comment_id,
            "author": author,
            "content": content,
            "created_at": datetime.utcnow(),
        }

        COMMENTS.setdefault(post_id, []).append(comment)
        post["comments_count"] = len(COMMENTS[post_id])

        return JSONResponse(status_code=201, content={
            "message": "comment_created",
            "data": {
                "comment_id": comment_id,
                "comments_count": post["comments_count"],
                "comments_count_display": compact_count(post["comments_count"])
            }
        })

    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })


def update_comment(post_id: int, comment_id: int, payload: dict | None):
    """
    PATCH /posts/{post_id}/comments/{comment_id}
    댓글 수정
    """
    try:
        content = (payload or {}).get("content")
        if not content:
            return JSONResponse(status_code=400, content={
                "message": "invalid_request",
                "data": None
            })

        if len(content) > 500:
            return JSONResponse(status_code=422, content={
                "message": "validation_error",
                "data": None
            })

        comments = COMMENTS.get(post_id)
        if comments is None:
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None
            })

        comment = next((c for c in comments if c["id"] == comment_id), None)
        if not comment:
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None
            })

        comment["content"] = content

        return JSONResponse(content={
            "message": "comment_updated",
            "data": {
                "comment_id": comment_id
            }
        })

    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })


def delete_comment(post_id: int, comment_id: int):
    """
    DELETE /posts/{post_id}/comments/{comment_id}
    댓글 삭제
    """
    try:
        comments = COMMENTS.get(post_id)
        if comments is None:
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None
            })

        idx = next((i for i, c in enumerate(comments) if c["id"] == comment_id), None)
        if idx is None:
            return JSONResponse(status_code=404, content={
                "message": "not_found",
                "data": None
            })

        comments.pop(idx)
        post = next((p for p in POSTS if p["id"] == post_id), None)
        if post:
            post["comments_count"] = len(comments)

        return JSONResponse(content={
            "message": "comment_deleted",
            "data": {
                "comments_count": len(comments),
                "comments_count_display": compact_count(len(comments))
            }
        })

    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })
