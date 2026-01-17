"""
Stocks API Dependency Injection
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.stock_data.repository import StockRepository

def get_stock_repo(db: Session = Depends(get_db)) -> StockRepository:
    """取得 Stock Repository 實例"""
    # TODO: 這裡還沒有整合 Redis，Phase 3.3 測試有用到 Mock Redis，生產環境需要連線
    # 目前先傳 None 或實作 Redis dependency
    return StockRepository(db, redis=None)
