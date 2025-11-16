from fastapi import APIRouter, Form, File, UploadFile
from fastapi.responses import JSONResponse

from controllers.makepost_controller import makepost_meta, create_post

router = APIRouter(prefix="/posts", tags=["MakePost"])

@router.get("/new/meta")
def get_makepost_meta():
    try:
        return makepost_meta()
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })


@router.post("")
async def make_post(
    title: str = Form(...),
    body: str = Form(...),
    image: UploadFile | None = File(None)
):
    try:
        return await create_post(title, body, image)
    except Exception:
        return JSONResponse(status_code=500, content={
            "message": "internal_server_error",
            "data": None
        })
