"""
TDD 測試: 交易時機 (N/N+1)
- N_CLOSE: 訊號觸發當日收盤成交
- N1_OPEN: 訊號觸發隔日開盤成交
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from app.modules.backtest.engine import BacktestEngine, BacktestConfig

@pytest.fixture
def sample_data():
    """5 天測試資料"""
    dates = pd.date_range(start='2024-01-01', periods=5)
    data = pd.DataFrame({
        'open': [100.0, 102.0, 104.0, 106.0, 108.0],
        'high': [105.0, 107.0, 109.0, 111.0, 113.0],
        'low': [99.0, 101.0, 103.0, 105.0, 107.0],
        'close': [101.0, 103.0, 105.0, 107.0, 109.0],
        'volume': [1000] * 5
    }, index=dates)
    return data

def test_timing_n_close(sample_data):
    """測試 N_CLOSE: 訊號當日收盤成交"""
    config = BacktestConfig(
        initial_capital=100000,
        ticker="TEST",
        timing="N_CLOSE"  # 新增 timing 參數
    )
    engine = BacktestEngine(config)
    
    # Day 1 觸發進場訊號
    entry_signal = pd.Series([False, True, False, False, False], index=sample_data.index)
    exit_signal = pd.Series([False, False, False, True, False], index=sample_data.index)
    
    result = engine.run(sample_data, entry_signal, exit_signal)
    
    # 應該在 Day 1 的收盤價 103.0 買入
    assert len(result.trades) >= 1
    buy_trade = result.trades[0]
    assert buy_trade.price == 103.0  # Day 1 close

def test_timing_n1_open(sample_data):
    """測試 N1_OPEN: 訊號隔日開盤成交"""
    config = BacktestConfig(
        initial_capital=100000,
        ticker="TEST",
        timing="N1_OPEN"  # 隔日開盤
    )
    engine = BacktestEngine(config)
    
    # Day 1 觸發進場訊號
    entry_signal = pd.Series([False, True, False, False, False], index=sample_data.index)
    exit_signal = pd.Series([False, False, False, True, False], index=sample_data.index)
    
    result = engine.run(sample_data, entry_signal, exit_signal)
    
    # 應該在 Day 2 的開盤價 104.0 買入
    assert len(result.trades) >= 1
    buy_trade = result.trades[0]
    assert buy_trade.price == 104.0  # Day 2 open

def test_timing_default_is_n_close(sample_data):
    """測試預設值應為 N_CLOSE"""
    config = BacktestConfig(
        initial_capital=100000,
        ticker="TEST"
        # 不指定 timing，應該預設為 N_CLOSE
    )
    engine = BacktestEngine(config)
    
    entry_signal = pd.Series([False, True, False, False, False], index=sample_data.index)
    exit_signal = pd.Series([False, False, False, True, False], index=sample_data.index)
    
    result = engine.run(sample_data, entry_signal, exit_signal)
    
    # 預設應使用收盤價
    assert len(result.trades) >= 1
    buy_trade = result.trades[0]
    assert buy_trade.price == 103.0  # Day 1 close
