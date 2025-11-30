# main.py
from fastapi import FastAPI


from database import Base, engine
from db_models import User, Post, Comment 
from routers.user_router import router as user_router
from routers.post_router import router as post_router

app = FastAPI()

# 데모용: 앱 시작 시 테이블 생성
Base.metadata.create_all(bind=engine)

app.include_router(post_router)
app.include_router(user_router)
