from datetime import datetime, timedelta
import itertools
from typing import Optional, Dict

from .ai_model import check_toxic          # ✅ 같은 폴더 내부
#from ._storage import POSTS, COMMENTS, COMMENT_ID_SEQ, POST_ID_SEQ  # ✅ 같은 폴더 내부
#from ._utils import compact_count

def seed_posts(n: int = 10):
    base = datetime(2023, 11, 3, 12, 0, 0)
    posts = []
    for i in range(1, n + 1):
        posts.append({
            "id": i,
            "title": f"게시글 제목 {i} - 이것은 데모용 긴 제목입니다 (테스트 {i})",
            "body": f"게시글 {i}의 상세 내용입니다. (상세 페이지용 더미 텍스트)",
            "created_at": base + timedelta(minutes=i * 7),
            "comments_count": 0,
            "views": i * 157,
            "author": f"user{i%7 or 7}",
            "image_filename": None,
        })
    return posts


POSTS = seed_posts()
COMMENTS: Dict[int, list[dict]] = {p["id"]: [] for p in POSTS}
LIKES: Dict[int, dict] = {p["id"]: {"count": 0, "users": set()} for p in POSTS}

COMMENT_ID_SEQ = itertools.count(start=1)
POST_ID_SEQ = itertools.count(start=len(POSTS) + 1)

DEFAULT_CARD_COLOR = "#ACA0EB"
HOVER_CARD_COLOR   = "#7F6AEE"

LIKE_DEFAULT_COLOR = "#D9D9D9"
LIKE_ACTIVE_COLOR  = "#ACA0EB"

MAX_TITLE_LEN = 26


def truncate_title(title: str, max_len: int = 26) -> str:
    return title if len(title) <= max_len else title[:max_len]


def fmt_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def compact_count(n: int) -> str:
    if n >= 100_000:
        return "100k"
    if n >= 10_000:
        return "10k"
    if n >= 1_000:
        return "1k"
    return str(n)


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
# Model 함수 (dict만 반환)
# -----------------------------

def go_write_model() -> dict:
    return {
        "message": "go_write",
        "data": {"write_url": "/posts/new"},
    }


def posts_meta_model() -> dict:
    return {
        "message": "meta_ok",
        "data": {
            "colors": {"default": DEFAULT_CARD_COLOR, "hover": HOVER_CARD_COLOR},
            "write_url": "/posts/new",
        },
    }


def list_posts_model(cursor: int, limit: int) -> dict:
    total = len(POSTS)
    end = min(cursor + limit, total)
    items = [shape_card(p) for p in POSTS[cursor:end]]
    next_cursor = end if end < total else None

    return {
        "message": "list_ok",
        "data": {
            "items": items,
            "next_cursor": next_cursor,
            "total": total,
        },
    }


def get_post_detail_model(post_id: int) -> dict:
    post = next((p for p in POSTS if p["id"] == post_id), None)
    if not post:
        return {"message": "not_found", "data": None}

    post["views"] += 1

    comments = COMMENTS.get(post_id, [])
    likes_info = LIKES.get(post_id, {"count": 0, "users": set()})

    return {
        "message": "detail_ok",
        "data": {
            "id": post["id"],
            "title": post["title"],
            "body": post["body"],           # LONGTEXT에 해당
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
                    "created_at": fmt_datetime(c["created_at"]),
                }
                for c in comments
            ],
        },
    }


def toggle_like_model(post_id: int, payload: Optional[dict]) -> dict:
    user_id = (payload or {}).get("user_id")
    if user_id is None:
        return {"message": "invalid_request", "data": None}

    post = next((p for p in POSTS if p["id"] == post_id), None)
    if not post:
        return {"message": "not_found", "data": None}

    like_info = LIKES.setdefault(post_id, {"count": 0, "users": set()})
    users = like_info["users"]

    if user_id in users:
        users.remove(user_id)
        like_info["count"] = max(0, like_info["count"] - 1)
        liked = False
    else:
        users.add(user_id)
        like_info["count"] += 1
        liked = True

    return {
        "message": "like_toggled",
        "data": {
            "liked": liked,
            "likes": like_info["count"],
            "button_color": LIKE_ACTIVE_COLOR if liked else LIKE_DEFAULT_COLOR,
        },
    }


def list_comments_model(post_id: int) -> dict:
    post = next((p for p in POSTS if p["id"] == post_id), None)
    if not post:
        return {"message": "not_found", "data": None}

    comments = COMMENTS.get(post_id, [])

    return {
        "message": "comments_ok",
        "data": {
            "comments_count": len(comments),
            "comments_count_display": compact_count(len(comments)),
            "items": [
                {
                    "comment_id": c["id"],
                    "author": c["author"],
                    "content": c["content"],
                    "created_at": fmt_datetime(c["created_at"]),
                }
                for c in comments
            ],
        },
    }


def create_comment_model(post_id: int, payload: Optional[dict]) -> dict:
    author = (payload or {}).get("author", "anonymous")
    content = (payload or {}).get("content")

    if not content:
        return {"message": "invalid_request", "data": None}

    if len(content) > 500:
        return {"message": "validation_error", "data": None}

    moderation = check_toxic(content, threshold=0.7)

    if not moderation["success"]:
        # AI 모델 자체 문제 (로딩 실패, 추론 실패 등)
        return {
            "message": "ai_error",
            "data": {
                "reason": "ai_inference_failed",
                "error": moderation["error"],
            },
        }

    if moderation["is_toxic"]:
        # 욕설/비도덕적 게시글 → 차단
        return {
            "message": "blocked_toxic_post",
            "data": {
                "reason": "toxic_content",
                "model_label": moderation["label"],
                "score": moderation["score"],
            },
        }



    post = next((p for p in POSTS if p["id"] == post_id), None)
    if not post:
        return {"message": "not_found", "data": None}

    comment_id = next(COMMENT_ID_SEQ)
    comment = {
        "id": comment_id,
        "author": author,
        "content": content,
        "created_at": datetime.utcnow(),
    }

    COMMENTS.setdefault(post_id, []).append(comment)
    post["comments_count"] = len(COMMENTS[post_id])

    return {
        "message": "comment_created",
        "data": {
            "comment_id": comment_id,
            "comments_count": post["comments_count"],
            "comments_count_display": compact_count(post["comments_count"]),
        },
    }


def update_comment_model(post_id: int, comment_id: int, payload: Optional[dict]) -> dict:
    content = (payload or {}).get("content")
    if not content:
        return {"message": "invalid_request", "data": None}

    if len(content) > 500:
        return {"message": "validation_error", "data": None}

    # AI 검사
    moderation = moderate_text_model(content)

    moderation = check_toxic(content, threshold=0.7)

    if not moderation["success"]:
        # AI 모델 자체 문제 (로딩 실패, 추론 실패 등)
        return {
            "message": "ai_error",
            "data": {
                "reason": "ai_inference_failed",
                "error": moderation["error"],
            },
        }

    if moderation["is_toxic"]:
        # 욕설/비도덕적 게시글 → 차단
        return {
            "message": "blocked_toxic_post",
            "data": {
                "reason": "toxic_content",
                "model_label": moderation["label"],
                "score": moderation["score"],
            },
        }

    comments = COMMENTS.get(post_id)
    if comments is None:
        return {"message": "not_found", "data": None}

    comment = next((c for c in comments if c["id"] == comment_id), None)
    if not comment:
        return {"message": "not_found", "data": None}

    comment["content"] = content

    return {
        "message": "comment_updated",
        "data": {
            "comment_id": comment_id,
        },
    }


def delete_comment_model(post_id: int, comment_id: int) -> dict:
    comments = COMMENTS.get(post_id)
    if comments is None:
        return {"message": "not_found", "data": None}

    idx = next((i for i, c in enumerate(comments) if c["id"] == comment_id), None)
    if idx is None:
        return {"message": "not_found", "data": None}

    comments.pop(idx)
    post = next((p for p in POSTS if p["id"] == post_id), None)
    if post:
        post["comments_count"] = len(comments)

    return {
        "message": "comment_deleted",
        "data": {
            "comments_count": len(comments),
            "comments_count_display": compact_count(len(comments)),
        },
    }


def makepost_meta_model() -> dict:
    return {
        "message": "meta_ok",
        "data": {
            "max_title_length": MAX_TITLE_LEN,
            "colors": {
                "default": "#ACA0EB",
                "active": "#7F6AEE",
            },
            "helper_text": {
                "title_rule": "*제목은 최대 26자까지 작성 가능합니다.",
                "title_required": "*제목을 입력해주세요.",
                "body_required": "*내용을 입력해주세요.",
            },
        },
    }


def create_post_model(title: str, body: str,
                      image_info: Optional[dict]) -> dict:
    title = title.strip()
    body = body.strip()

    if not title or not body:
        return {"message": "invalid_request", "data": None}

    if len(title) > MAX_TITLE_LEN:
        return {
            "message": "validation_error",
            "data": {"field": "title", "reason": "too_long"},
        }

    moderation = check_toxic(f"{title}\n{body}", threshold=0.7)

    if not moderation["success"]:
        # AI 모델 자체 문제 (로딩 실패, 추론 실패 등)
        return {
            "message": "ai_error",
            "data": {
                "reason": "ai_inference_failed",
                "error": moderation["error"],
            },
        }

    if moderation["is_toxic"]:
        # 욕설/비도덕적 게시글 → 차단
        return {
            "message": "blocked_toxic_post",
            "data": {
                "reason": "toxic_content",
                "model_label": moderation["label"],
                "score": moderation["score"],
            },
        }

    image_filename = None
    if image_info is not None:
        content_type = image_info.get("content_type") or ""
        if not content_type.startswith("image/"):
            return {
                "message": "validation_error",
                "data": {"field": "image", "reason": "not_image"},
            }
        image_filename = image_info.get("filename")


    new_id = next(POST_ID_SEQ)
    now = datetime.utcnow()

    new_post = {
        "id": new_id,
        "title": title,
        "body": body,  # LONGTEXT 컬럼에 매핑된다고 가정
        "created_at": now,
        "comments_count": 0,
        "views": 0,
        "author": "user1",        # 데모용
        "image_filename": image_filename,
    }

    POSTS.append(new_post)
    COMMENTS[new_id] = []
    LIKES[new_id] = {"count": 0, "users": set()}

    return {
        "message": "post_created",
        "data": {
            "post_id": new_id,
            "detail_url": f"/posts/{new_id}",
            "button_color": "#7F6AEE",
        },
    }


def editpost_meta_model(post_id: int) -> dict:
    post = next((p for p in POSTS if p["id"] == post_id), None)
    if not post:
        return {"message": "not_found", "data": None}

    image = None
    if post.get("image_filename"):
        image = {
            "filename": post["image_filename"],
            "url": f"/static/uploads/{post['image_filename']}",
        }

    return {
        "message": "edit_meta_ok",
        "data": {
            "post": {
                "id": post["id"],
                "title": post["title"],
                "body": post["body"],
                "created_at": fmt_datetime(post["created_at"]),
                "author": post["author"],
                "image": image,
            },
            "max_title_length": MAX_TITLE_LEN,
            "helper_text": {
                "title_rule": "*제목은 최대 26자까지 작성 가능합니다.",
                "title_required": "*제목을 입력해주세요.",
                "body_required": "*내용을 입력해주세요.",
            },
        },
    }


def update_post_model(
    post_id: int,
    title: str,
    body: str,
    image_info: Optional[dict],
    remove_image: bool,
) -> dict:
    post = next((p for p in POSTS if p["id"] == post_id), None)
    if not post:
        return {"message": "not_found", "data": None}

    title = title.strip()
    body = body.strip()

    if not title or not body:
        return {"message": "invalid_request", "data": None}

    if len(title) > MAX_TITLE_LEN:
        return {
            "message": "validation_error",
            "data": {"field": "title", "reason": "too_long"},
        }

    moderation = check_toxic(f"{title}\n{body}", threshold=0.7)

    if not moderation["success"]:
        # AI 모델 자체 문제 (로딩 실패, 추론 실패 등)
        return {
            "message": "ai_error",
            "data": {
                "reason": "ai_inference_failed",
                "error": moderation["error"],
            },
        }

    if moderation["is_toxic"]:
        # 욕설/비도덕적 게시글 → 차단
        return {
            "message": "blocked_toxic_post",
            "data": {
                "reason": "toxic_content",
                "model_label": moderation["label"],
                "score": moderation["score"],
            },
        }




    if image_info is not None:
        content_type = image_info.get("content_type") or ""
        if not content_type.startswith("image/"):
            return {
                "message": "validation_error",
                "data": {"field": "image", "reason": "not_image"},
            }
        post["image_filename"] = image_info.get("filename")
    elif remove_image:
        post["image_filename"] = None

    post["title"] = title
    post["body"] = body

    return {
        "message": "post_updated",
        "data": {
            "post_id": post_id,
            "detail_url": f"/posts/{post_id}",
        },
    }
