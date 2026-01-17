"""
FastAPI 應用程式入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.database import Base, engine

# 建立資料庫表格 (Dev only)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LazyBacktest API",
    description="Backend API for LazyBacktest Engine",
    version="0.1.0",
)

# CORS 設定
origins = [
    "http://localhost:3000",  # React Dev Server
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載 API 路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    """健康檢查端點"""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/")
def root():
    """根目錄"""
    return {"message": "Welcome to LazyBacktest API"}
