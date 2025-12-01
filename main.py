from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, admin, students, teachers

# FastAPIアプリケーション作成
app = FastAPI(
    title="HugHigh Login API",
    description="下妻第一高校 非認知能力可視化アプリ - ログイン機能",
    version="1.0.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(students.router)
app.include_router(teachers.router)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "HugHigh Login API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok"}
