"""
Backtest API 端點
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from datetime import date
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from app.api.deps import get_stock_repo
from app.modules.stock_data.repository import StockRepository
from app.modules.backtest.engine import BacktestEngine, BacktestConfig
from app.modules.backtest.indicators import sma

# 訊號生成器 (簡單實作，未來可擴充為動態策略載入)
from app.modules.backtest.signals import golden_cross

router = APIRouter()


# Request Models
# Request Models
class StrategyConfigV2(BaseModel):
    entry_strategy: str
    entry_params: Dict[str, Any] = {}
    exit_strategy: str = "SAME_AS_ENTRY"
    exit_params: Dict[str, Any] = {}

class TradingSettings(BaseModel):
    timing: str = "N_CLOSE"
    buy_fee: float = 0.001425
    sell_fee: float = 0.004425
    tax: float = 0.003

class RiskSettings(BaseModel):
    position_basis: str = "INITIAL_CAPITAL"
    position_pct: float = 100.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class BacktestRequest(BaseModel):
    ticker: str
    start_date: date
    end_date: date
    initial_capital: float = 100000
    trading_settings: Optional[TradingSettings] = None
    risk_settings: Optional[RiskSettings] = None
    strategy_settings: StrategyConfigV2
    # 相容舊版參數
    strategy: Optional[Any] = None 

class OptimizationRequest(BaseModel):
    ticker: str
    start_date: date
    end_date: date
    initial_capital: float = 100000
    entry_strategy: str
    param_ranges: Dict[str, List[Any]]


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
    buy_fee = 0.001425
    sell_fee = 0.001425
    tax = 0.003
    stop_loss = None
    take_profit = None
    timing = "N_CLOSE"
    position_pct = 100.0
    position_basis = "INITIAL_CAPITAL"

    if request.trading_settings:
        buy_fee = request.trading_settings.buy_fee
        sell_fee = request.trading_settings.sell_fee
        tax = request.trading_settings.tax
        timing = request.trading_settings.timing
    
    if request.risk_settings:
        stop_loss = request.risk_settings.stop_loss
        take_profit = request.risk_settings.take_profit
        position_pct = request.risk_settings.position_pct
        position_basis = request.risk_settings.position_basis

    config = BacktestConfig(
        initial_capital=request.initial_capital,
        ticker=request.ticker,
        buy_fee=buy_fee,
        sell_fee=sell_fee,
        tax=tax,
        stop_loss=stop_loss,
        take_profit=take_profit,
        timing=timing,
        position_pct=position_pct,
        position_basis=position_basis
    )
    
    engine = BacktestEngine(config)
    
    # 3. 產生策略訊號 (使用 StrategyRegistry)
    from app.modules.backtest.strategies import StrategyRegistry
    
    # 處理進出場策略分離
    try:
        entry_signal, default_exit = StrategyRegistry.get_signals(
            request.strategy_settings.entry_strategy, 
            df, 
            request.strategy_settings.entry_params
        )
        
        if request.strategy_settings.exit_strategy == "SAME_AS_ENTRY":
            exit_signal = default_exit
        else:
            _, exit_signal = StrategyRegistry.get_signals(
                request.strategy_settings.exit_strategy,
                df,
                request.strategy_settings.exit_params
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # 4. 執行回測
    result = engine.run(df, entry_signal, exit_signal)
    
    # 計算進階指標
    from app.modules.backtest.metrics import (
        calculate_sharpe_ratio, calculate_sortino_ratio,
        calculate_yearly_returns, calculate_monthly_returns, calculate_buy_hold_return,
        calculate_average_trade, calculate_max_consecutive_wins, calculate_max_consecutive_losses,
        calculate_overfitting_ratio, calculate_period_performance
    )
    
    # 計算每日報酬率
    daily_returns = result.equity_curve.pct_change().dropna()
    sharpe = calculate_sharpe_ratio(daily_returns)
    sortino = calculate_sortino_ratio(daily_returns)
    yearly_returns = calculate_yearly_returns(result.equity_curve)
    monthly_returns = calculate_monthly_returns(result.equity_curve)
    buy_hold_return = calculate_buy_hold_return(df)
    
    # 計算交易統計
    profits = [t.profit for t in result.trades if t.profit is not None]
    avg_trade_pnl = calculate_average_trade(profits)
    max_consecutive_wins = calculate_max_consecutive_wins(profits)
    max_consecutive_losses = calculate_max_consecutive_losses(profits)
    
    # 計算 Buy & Hold 淨值曲線 (用於雙線對照圖)
    initial_price = df['close'].iloc[0]
    buy_hold_equity = (df['close'] / initial_price) * request.initial_capital
    
    # 計算過度配適比率 (Phase 11 P1)
    overfitting_ratio = calculate_overfitting_ratio(
        strategy_return=result.total_return,
        buy_hold_return=buy_hold_return,
        strategy_sharpe=sharpe if not (pd.isna(sharpe) or np.isinf(sharpe)) else None,
        buy_hold_sharpe=None  # Buy & Hold 的 Sharpe 需要額外計算，暫時不提供
    )
    
    # 計算期間績效 (Phase 11 P1)
    period_performance = calculate_period_performance(
        equity_curve=result.equity_curve,
        buy_hold_curve=buy_hold_equity,
        initial_capital=request.initial_capital
    )

    # 5. 回傳結果
    return {
        "ticker": request.ticker,
        "total_return": result.total_return,
        "cagr": result.cagr,
        "max_drawdown": result.max_drawdown,
        "win_rate": result.win_rate,
        "sharpe_ratio": 0.0 if pd.isna(sharpe) or np.isinf(sharpe) else sharpe,
        "sortino_ratio": 0.0 if pd.isna(sortino) or np.isinf(sortino) else sortino,
        "buy_hold_return": buy_hold_return,
        "avg_trade_pnl": avg_trade_pnl,
        "max_consecutive_wins": max_consecutive_wins,
        "max_consecutive_losses": max_consecutive_losses,
        "yearly_returns": yearly_returns,
        "monthly_returns": monthly_returns,
        "total_trades": result.total_trades,
        "final_capital": result.final_capital,
        "trades": [
            {
                "date": t.date.strftime("%Y-%m-%d") if hasattr(t.date, 'strftime') else str(t.date),
                "action": t.action,
                "price": t.price,
                "quantity": t.quantity,
                "profit": t.profit
            } for t in result.trades
        ],
        "equity_curve": [
            {
                "date": date_idx.strftime("%Y-%m-%d"),
                "equity": float(equity),
                "return_pct": float((equity / request.initial_capital - 1) * 100),
                "drawdown": float(0.0)
            } for date_idx, equity in result.equity_curve.items()
        ],
        "buy_hold_curve": [
            {
                "date": date_idx.strftime("%Y-%m-%d"),
                "equity": float(equity),
                "return_pct": float((equity / request.initial_capital - 1) * 100)
            } for date_idx, equity in buy_hold_equity.items()
        ],
        "overfitting_ratio": overfitting_ratio,
        "period_performance": period_performance
    }


@router.post("/optimize")
def run_optimization(
    request: OptimizationRequest,
    repo: StockRepository = Depends(get_stock_repo)
):
    """
    執行參數優化
    """
    # 1. 取得股價資料
    df = repo.get_stock_data(request.ticker, request.start_date, request.end_date)
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for optimization")
    
    # 2. 執行優化 (使用 optimization 模組)
    from app.modules.backtest.optimization import grid_search
    
    try:
        results = grid_search(
            request.entry_strategy,
            request.param_ranges,
            df,
            initial_capital=request.initial_capital
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # 3. 回傳結果
    return {
        "ticker": request.ticker,
        "strategy": request.entry_strategy,
        "results_count": len(results),
        "results": results
    }
