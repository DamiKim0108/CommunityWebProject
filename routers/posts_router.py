# routers/posts_router.py

from fastapi import APIRouter, Query, Body
from fastapi.responses import JSONResponse

from controllers.posts_controller import (
    go_write as go_write_service,
    posts_meta as posts_meta_service,
    list_posts as list_posts_service,
    get_post_detail as get_post_detail_service,
    toggle_like as toggle_like_service,
    list_comments as list_comments_service,
    create_comment as create_comment_service,
    update_comment as update_comment_service,
    delete_comment as delete_comment_service,
)

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/new")
def go_write():
    """
    새 글쓰기 페이지로 이동용 메타 정보
    """
    try:
        return go_write_service()
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "message": "internal_server_error",
                "data": None,
            },
        )


@router.get("/meta")
def posts_meta():
    """
    목록 페이지 UI용 색상, 작성 URL 등 메타 데이터
    """
    try:
        return posts_meta_service()
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "message": "internal_server_error",
                "data": None,
            },
        )


@router.get("")
def list_posts(
    cursor: int = Query(
        0,
        ge=0,
        description="다음 페이지의 시작 인덱스(오프셋)",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="페이지 크기(1~50)",
    ),
):
    """
    게시글 목록(무한 스크롤) 조회
    """
    try:
        return list_posts_service(cursor=cursor, limit=limit)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "message": "internal_server_error",
                "data": None,
            },
        )


@router.get("/{post_id}")
def get_post_detail(post_id: int):
    """
    게시글 상세 조회
    """
    try:
        return get_post_detail_service(post_id=post_id)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "message": "internal_server_error",
                "data": None,
            },
        )


@router.post("/{post_id}/like")
def toggle_like(post_id: int, payload: dict | None = Body(None)):
    """
    좋아요 토글
    """
    try:
        return toggle_like_service(post_id=post_id, payload=payload)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "message": "internal_server_error",
                "data": None,
            },
        )


@router.get("/{post_id}/comments")
def list_comments(post_id: int):
    """
    댓글 목록 조회
    """
    try:
        return list_comments_service(post_id=post_id)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "message": "internal_server_error",
                "data": None,
            },
        )


@router.post("/{post_id}/comments")
def create_comment(post_id: int, payload: dict | None = Body(None)):
    """
    댓글 작성
    """
    try:
        return create_comment_service(post_id=post_id, payload=payload)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "message": "internal_server_error",
                "data": None,
            },
        )


@router.patch("/{post_id}/comments/{comment_id}")
def update_comment(
    post_id: int,
    comment_id: int,
    payload: dict | None = Body(None),
):
    """
    댓글 수정
    """
    try:
        return update_comment_service(
            post_id=post_id,
            comment_id=comment_id,
            payload=payload,
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "message": "internal_server_error",
                "data": None,
            },
        )


@router.delete("/{post_id}/comments/{comment_id}")
def delete_comment(post_id: int, comment_id: int):
    """
    댓글 삭제
    """
    try:
        return delete_comment_service(
            post_id=post_id,
            comment_id=comment_id,
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "message": "internal_server_error",
                "data": None,
            },
        )
