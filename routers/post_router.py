# routers/post_router.py
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from database import get_db
from controllers.post_controller import (
    list_posts_controller,
    get_post_detail_controller,
    create_post_controller,
    create_comment_controller,
)

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("")
def list_posts(
    cursor: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return list_posts_controller(db, cursor, limit)


@router.get("/{post_id}")
def get_post_detail(
    post_id: int,
    db: Session = Depends(get_db),
):
    return get_post_detail_controller(db, post_id)


@router.post("")
def create_post(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    """
    Body 예시:
    {
      "author_id": 1,
      "title": "제목",
      "body": "내용"
    }
    """
    author_id = payload.get("author_id")
    return create_post_controller(db, author_id, payload)


@router.post("/{post_id}/comments")
def create_comment(
    post_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    """
    Body 예시:
    {
      "author_id": 1,
      "content": "댓글 내용"
    }
    """
    return create_comment_controller(db, post_id, payload)
