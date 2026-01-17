import pytest
import pandas as pd
import numpy as np
from app.modules.backtest.strategies import StrategyRegistry

@pytest.fixture
def sample_data():
    """建立模擬股價資料"""
    dates = pd.date_range(start='2024-01-01', periods=100)
    data = pd.DataFrame({
        'date': dates,
        'open': np.linspace(100, 110, 100),
        'high': np.linspace(105, 115, 100),
        'low': np.linspace(95, 105, 100),
        'close': np.linspace(100, 110, 100),
        'volume': np.random.randint(1000, 5000, 100)
    })
    return data

def test_registry_get_strategy_names():
    """測試獲取所有策略名稱"""
    names = StrategyRegistry.get_all_strategy_names()
    assert "SMA_CROSS" in names
    assert "RSI_OVERSOLD" in names
    assert "MACD_CROSS" in names

def test_registry_get_signals_sma_cross(sample_data):
    """測試 SMA_CROSS 訊號產生"""
    params = {"short_period": 5, "long_period": 20}
    entry_signal, exit_signal = StrategyRegistry.get_signals(
        "SMA_CROSS", sample_data, params
    )
    
    assert len(entry_signal) == len(sample_data)
    assert entry_signal.dtype == bool

def test_registry_get_signals_rsi(sample_data):
    """測試 RSI_OVERSOLD 訊號產生"""
    params = {"period": 14, "threshold": 30}
    entry, exit = StrategyRegistry.get_signals("RSI_OVERSOLD", sample_data, params)
    assert len(entry) == len(sample_data)

def test_registry_get_signals_macd(sample_data):
    """測試 MACD_CROSS 訊號產生"""
    params = {"fast_period": 12, "slow_period": 26, "signal_period": 9}
    entry, exit = StrategyRegistry.get_signals("MACD_CROSS", sample_data, params)
    assert len(entry) == len(sample_data)

def test_registry_get_signals_kd(sample_data):
    """測試 KD_CROSS 訊號產生"""
    params = {"period": 9, "k_smooth": 3, "d_smooth": 3}
    entry, exit = StrategyRegistry.get_signals("KD_CROSS", sample_data, params)
    assert len(entry) == len(sample_data)

def test_registry_get_signals_bollinger(sample_data):
    """測試 BOLLINGER_BREAKOUT 訊號產生"""
    params = {"period": 20, "std_dev": 2.0}
    entry, exit = StrategyRegistry.get_signals("BOLLINGER_BREAKOUT", sample_data, params)
    assert len(entry) == len(sample_data)

def test_registry_get_signals_price_breakout(sample_data):
    """測試 PRICE_BREAKOUT 訊號產生"""
    params = {"period": 20}
    entry, exit = StrategyRegistry.get_signals("PRICE_BREAKOUT", sample_data, params)
    assert len(entry) == len(sample_data)

def test_registry_invalid_strategy():
    """測試無效策略名稱"""
    with pytest.raises(ValueError, match="Unknown strategy"):
        StrategyRegistry.get_signals("INVALID_STRATEGY", pd.DataFrame(), {})

def test_registry_missing_params(sample_data):
    """測試缺少參數時的行為 (應該使用預設值或拋出異常)"""
    # 假設我們要求明確傳入參數
    with pytest.raises(ValueError, match="Missing required parameter"):
        StrategyRegistry.get_signals("SMA_CROSS", sample_data, {})
