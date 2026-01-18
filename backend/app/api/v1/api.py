"""
API 路由配置 (v1)
"""
from fastapi import APIRouter

api_router = APIRouter()

# 這裡未來會掛載 stocks, backtest 等路由
from app.api.v1.endpoints import stocks, backtest

api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
api_router.include_router(backtest.router, prefix="/backtest", tags=["backtest"])

@api_router.get("/health")
def health_check():
    """API Health Check"""
    return {"status": "ok", "version": "0.1.0"}
