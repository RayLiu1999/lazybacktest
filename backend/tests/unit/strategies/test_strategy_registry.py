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
    # 驗證新策略
    assert "SMA_DEATH_CROSS" in names
    assert "PRICE_CROSS_SMA" in names
    assert "RSI_OVERBOUGHT" in names
    assert "MACD_CROSS_DOWN" in names
    assert "KD_CROSS_DOWN" in names
    assert "BOLLINGER_REVERSAL" in names
    assert "TURTLE_BREAKOUT" in names

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

def test_registry_missing_params_uses_defaults(sample_data):
    """測試缺少參數時自動套用預設值"""
    # SMA_CROSS 預設值: short_period=5, long_period=20
    entry, exit = StrategyRegistry.get_signals("SMA_CROSS", sample_data, {})
    assert len(entry) == len(sample_data)
    assert entry.dtype == bool


# ========== 新策略測試 ==========

def test_registry_get_signals_sma_death_cross(sample_data):
    """測試 SMA_DEATH_CROSS 訊號產生"""
    params = {"short_period": 5, "long_period": 20}
    entry, exit = StrategyRegistry.get_signals("SMA_DEATH_CROSS", sample_data, params)
    assert len(entry) == len(sample_data)
    assert entry.dtype == bool
    assert exit.dtype == bool

def test_registry_get_signals_price_cross_sma(sample_data):
    """測試 PRICE_CROSS_SMA 訊號產生"""
    params = {"period": 20}
    entry, exit = StrategyRegistry.get_signals("PRICE_CROSS_SMA", sample_data, params)
    assert len(entry) == len(sample_data)
    assert entry.dtype == bool

def test_registry_get_signals_rsi_overbought(sample_data):
    """測試 RSI_OVERBOUGHT 訊號產生"""
    params = {"period": 14, "threshold": 70}
    entry, exit = StrategyRegistry.get_signals("RSI_OVERBOUGHT", sample_data, params)
    assert len(entry) == len(sample_data)
    assert entry.dtype == bool

def test_registry_get_signals_macd_cross_down(sample_data):
    """測試 MACD_CROSS_DOWN 訊號產生"""
    params = {"fast_period": 12, "slow_period": 26, "signal_period": 9}
    entry, exit = StrategyRegistry.get_signals("MACD_CROSS_DOWN", sample_data, params)
    assert len(entry) == len(sample_data)
    assert entry.dtype == bool

def test_registry_get_signals_kd_cross_down(sample_data):
    """測試 KD_CROSS_DOWN 訊號產生"""
    params = {"period": 9, "k_smooth": 3, "d_smooth": 3}
    entry, exit = StrategyRegistry.get_signals("KD_CROSS_DOWN", sample_data, params)
    assert len(entry) == len(sample_data)
    assert entry.dtype == bool

def test_registry_get_signals_bollinger_reversal(sample_data):
    """測試 BOLLINGER_REVERSAL 訊號產生"""
    params = {"period": 20, "std_dev": 2.0}
    entry, exit = StrategyRegistry.get_signals("BOLLINGER_REVERSAL", sample_data, params)
    assert len(entry) == len(sample_data)
    assert entry.dtype == bool

def test_registry_get_signals_turtle_breakout(sample_data):
    """測試 TURTLE_BREAKOUT 訊號產生"""
    params = {"entry_period": 20, "exit_period": 10}
    entry, exit = StrategyRegistry.get_signals("TURTLE_BREAKOUT", sample_data, params)
    assert len(entry) == len(sample_data)
    assert entry.dtype == bool

def test_registry_strategy_aliases(sample_data):
    """測試策略別名映射"""
    # MACD_CROSS_UP 應該映射到 MACD_CROSS
    entry1, _ = StrategyRegistry.get_signals("MACD_CROSS_UP", sample_data, {})
    entry2, _ = StrategyRegistry.get_signals("MACD_CROSS", sample_data, {})
    assert (entry1 == entry2).all()
    
    # KD_CROSS_UP 應該映射到 KD_CROSS
    entry3, _ = StrategyRegistry.get_signals("KD_CROSS_UP", sample_data, {})
    entry4, _ = StrategyRegistry.get_signals("KD_CROSS", sample_data, {})
    assert (entry3 == entry4).all()
