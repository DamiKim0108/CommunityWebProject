from fastapi import APIRouter, Form, File, UploadFile
from fastapi.responses import JSONResponse

from controllers.editpost_controller import (
    get_edit_post_meta as get_edit_post_meta_service,
    update_post as update_post_service,
)

router = APIRouter(prefix="/posts", tags=["EditPost"])

@router.get("/{post_id}/edit")
def get_edit_post(post_id: int):
    try:
        return get_edit_post_meta_service(post_id)
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })


@router.patch("/{post_id}")
async def edit_post(
    post_id: int,
    title: str = Form(...),
    body: str = Form(...),
    image: UploadFile | None = File(None),
    remove_image: str | None = Form(None),
):
    try:
        return await update_post_service(
            post_id=post_id,
            title=title,
            body=body,
            image=image,
            remove_image=remove_image,
        )
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })
