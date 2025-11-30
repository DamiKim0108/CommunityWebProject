# models/post_model.py
from typing import Optional, Dict, Any, List
from datetime import datetime

from sqlalchemy.orm import Session

from db_models import Post, Comment, User
from models.ai_model import check_toxic

MAX_TITLE_LEN = 26


def _compact_count(n: int) -> str:
    if n >= 100_000:
        return "100k"
    if n >= 10_000:
        return "10k"
    if n >= 1_000:
        return "1k"
    return str(n)


def get_post_list(db: Session, cursor: int, limit: int) -> Dict[str, Any]:
    total = db.query(Post).count()

    posts: List[Post] = (
        db.query(Post)
        .order_by(Post.id.asc())
        .offset(cursor)
        .limit(limit)
        .all()
    )

    next_cursor = cursor + limit
    if next_cursor >= total:
        next_cursor = None

    items = []
    for p in posts:
        items.append({
            "id": p.id,
            "title": p.title if len(p.title) <= MAX_TITLE_LEN else p.title[:MAX_TITLE_LEN],
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "comments": _compact_count(len(p.comments)),
            "views": _compact_count(p.views),
            "detail_url": f"/posts/{p.id}",
            "colors": {"default": "#ACA0EB", "hover": "#7F6AEE"},
        })

    return {
        "items": items,
        "total": total,
        "next_cursor": next_cursor,
    }


def get_post_detail(db: Session, post_id: int) -> Optional[Dict[str, Any]]:
    post: Optional[Post] = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return None

    # 조회수 +1
    post.views += 1
    db.add(post)
    db.commit()
    db.refresh(post)

    comments_data = []
    for c in post.comments:
        comments_data.append({
            "comment_id": c.id,
            "author": c.author.nickname if c.author else "unknown",
            "content": c.content,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "author": post.author.nickname if post.author else "unknown",
        "created_at": post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "views": post.views,
        "views_display": _compact_count(post.views),
        "comments_count": len(post.comments),
        "comments_count_display": _compact_count(len(post.comments)),
        "likes": 0,  # 아직 likes 테이블은 안 만들었으니 0으로 둠
        "comments": comments_data,
    }


def create_post(db: Session, author_id: int, title: str, body: str) -> Dict[str, Any]:
    title = (title or "").strip()
    body = (body or "").strip()

    if not title or not body:
        return {"error": "invalid_request"}

    if len(title) > MAX_TITLE_LEN:
        return {
            "error": "validation_error",
            "field": "title",
            "reason": "too_long",
        }

    # 작성자 존재 여부
    user = db.query(User).filter(User.id == author_id).first()
    if not user:
        return {"error": "user_not_found"}

    # AI 욕설/비도덕성 검사
    moderation = check_toxic(f"{title}\n{body}", threshold=0.7)
    if not moderation["success"]:
        return {"error": "ai_error", "detail": moderation["error"]}
    if moderation["is_toxic"]:
        return {
            "error": "blocked_toxic_post",
            "model_label": moderation["label"],
            "score": moderation["score"],
        }

    new_post = Post(
        title=title,
        body=body,
        author_id=author_id,
        created_at=datetime.utcnow(),
        views=0,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {
        "post_id": new_post.id,
        "detail_url": f"/posts/{new_post.id}",
    }


def create_comment(
    db: Session,
    post_id: int,
    author_id: int,
    content: str,
) -> Dict[str, Any]:
    content = (content or "").strip()
    if not content:
        return {"error": "invalid_request"}

    if len(content) > 500:
        return {"error": "validation_error"}

    # 게시글, 작성자 존재 여부
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return {"error": "not_found"}

    user = db.query(User).filter(User.id == author_id).first()
    if not user:
        return {"error": "user_not_found"}

    # AI 검사
    moderation = check_toxic(content, threshold=0.7)
    if not moderation["success"]:
        return {"error": "ai_error", "detail": moderation["error"]}
    if moderation["is_toxic"]:
        return {
            "error": "blocked_toxic_comment",
            "model_label": moderation["label"],
            "score": moderation["score"],
        }

    comment = Comment(
        post_id=post_id,
        author_id=author_id,
        content=content,
        created_at=datetime.utcnow(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    comments_count = db.query(Comment).filter(Comment.post_id == post_id).count()

    return {
        "comment_id": comment.id,
        "comments_count": comments_count,
        "comments_count_display": _compact_count(comments_count),
    }
