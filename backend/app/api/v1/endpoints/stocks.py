"""
Stocks API 端點
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date
from typing import List, Dict, Any

from app.modules.stock_data.repository import StockRepository
from app.api.deps import get_stock_repo

router = APIRouter()


@router.get("/{ticker}/history")
def get_stock_history(
    ticker: str,
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    repo: StockRepository = Depends(get_stock_repo)
) -> List[Dict[str, Any]]:
    """
    取得股票歷史資料 (K線圖)
    """
    df = repo.get_stock_data(ticker, start_date, end_date)
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found")
    
    # 將 DataFrame 轉為 JSON 友善格式 (List of Dicts)
    # DataFrame index 是 date，需要 reset_index 才能變成欄位
    result = df.reset_index().to_dict(orient="records")
    
    return result
