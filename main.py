from fastapi import FastAPI
from routers.signup_router import router as signup_router
from routers.login_router import router as login_router
from routers.posts_router import router as posts_router
from routers.profile_router import router as profile_router
from routers.makepost_router import router as makepost_router
app = FastAPI(title="Demo (Router Only Version)")

# 라우터 등록
app.include_router(signup_router)              # /users/signup ...
app.include_router(login_router)               # /users/login
app.include_router(posts_router)

app.include_router(profile_router)

app.include_router(makepost_router)