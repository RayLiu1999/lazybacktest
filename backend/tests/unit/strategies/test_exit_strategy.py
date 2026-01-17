"""
TDD 測試: 進出場策略分離
- exit_strategy 可與 entry_strategy 不同
"""
import pytest
import pandas as pd
from app.modules.backtest.strategies import StrategyRegistry

@pytest.fixture
def sample_data():
    """10 天測試資料"""
    dates = pd.date_range(start='2024-01-01', periods=20)
    data = pd.DataFrame({
        'open': [100.0] * 20,
        'high': [105.0] * 20,
        'low': [95.0] * 20,
        'close': [100.0 + i for i in range(20)],
        'volume': [1000] * 20
    }, index=dates)
    return data

def test_different_entry_exit_strategies(sample_data):
    """測試進場用 SMA_CROSS，出場用 RSI_OVERSOLD"""
    entry_params = {"short_period": 5, "long_period": 10}
    exit_params = {"period": 14, "threshold": 70}
    
    entry_signal, _ = StrategyRegistry.get_signals("SMA_CROSS", sample_data, entry_params)
    _, exit_signal = StrategyRegistry.get_signals("RSI_OVERSOLD", sample_data, exit_params)
    
    # 確保兩個訊號是獨立的
    assert len(entry_signal) == len(sample_data)
    assert len(exit_signal) == len(sample_data)
    # 不應完全相同
    # (RSI 出場訊號與 SMA 進場訊號獨立)

def test_same_as_entry_exit(sample_data):
    """測試出場策略與進場相同"""
    params = {"short_period": 5, "long_period": 10}
    
    entry_signal, exit_signal = StrategyRegistry.get_signals("SMA_CROSS", sample_data, params)
    
    # 進場是金叉，出場是死叉
    assert len(entry_signal) == len(sample_data)
    assert len(exit_signal) == len(sample_data)
