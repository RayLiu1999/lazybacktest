"""
Backtest API 端點
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from datetime import date
from typing import Dict, Any, List, Optional
import pandas as pd

from app.modules.stock_data.repository import StockRepository
from app.modules.backtest.engine import BacktestEngine, BacktestConfig
from app.modules.backtest.indicators import sma
from app.api.deps import get_stock_repo

# 訊號生成器 (簡單實作，未來可擴充為動態策略載入)
from app.modules.backtest.signals import golden_cross

router = APIRouter()


# Request Models
class StrategyParams(BaseModel):
    short_period: int = 5
    long_period: int = 20

class StrategyConfig(BaseModel):
    name: str
    params: Dict[str, Any] = {}

class BacktestRequest(BaseModel):
    ticker: str
    start_date: date
    end_date: date
    initial_capital: float = 100000
    buy_fee: float = 0.001425
    sell_fee: float = 0.001425
    tax: float = 0.003
    strategy: StrategyConfig


@router.post("/run")
def run_backtest(
    request: BacktestRequest,
    repo: StockRepository = Depends(get_stock_repo)
):
    """
    執行回測
    """
    # 1. 取得股價資料
    df = repo.get_stock_data(request.ticker, request.start_date, request.end_date)
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for backtest")
    
    # 2. 準備回測配置
    config = BacktestConfig(
        initial_capital=request.initial_capital,
        ticker=request.ticker,  # Added ticker
        buy_fee=request.buy_fee,
        sell_fee=request.sell_fee,
        tax=request.tax
    )
    
    engine = BacktestEngine(config)
    
    # 3. 產生策略訊號 (目前僅支援簡易 SMA 黃金交叉)
    # 未來應重構為 Strategy Pattern
    if request.strategy.name == "sma_crossover":
        short_p = request.strategy.params.get("short_period", 5)
        long_p = request.strategy.params.get("long_period", 20)
        
        # 計算指標
        sma_short = sma(df["close"], short_p)
        sma_long = sma(df["close"], long_p)
        
        # 產生訊號
        entry_signal = golden_cross(sma_short, sma_long)
        # 簡單策略：黃金交叉買進，由於 Engine 會自動處理賣出（停利損），這裡暫時不設特定出場訊號
        # 或是簡單設定：當發生死亡交叉時賣出？ 目前 BacktestEngine.run 是針對 entry/exit signal
        # 我們假設死亡交叉為出場
        # exit_signal = death_cross(sma_short, sma_long)
        # 簡化：暫時傳 False series, 讓它只靠 stop loss/profit 出場，或持有到底
        exit_signal = pd.Series(False, index=df.index)
        
    else:
        # Default strategy or raise error
        entry_signal = pd.Series(False, index=df.index)
        exit_signal = pd.Series(False, index=df.index)
        
    # 4. 執行回測
    result = engine.run(df, entry_signal, exit_signal)
    
    # 5. 回傳結果
    # 將結果轉換為 JSON 格式
    return {
        "ticker": request.ticker,
        "total_return": result.total_return,
        "cagr": result.cagr,
        "max_drawdown": result.max_drawdown,
        "win_rate": result.win_rate,
        "total_trades": result.total_trades,
        "final_capital": result.final_capital,
        "trades": [
            {
                "date": t.date,
                "type": t.type.value,
                "price": t.price,
                "quantity": t.quantity,
                "profit": t.profit
            } for t in result.trades
        ],
        "equity_curve": result.equity_curve
    }
