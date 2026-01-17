"""
TDD 測試: Buy & Hold 對照報酬
"""
import pytest
import pandas as pd
from app.modules.backtest.metrics import calculate_buy_hold_return

@pytest.fixture
def sample_data():
    """模擬股價從 100 漲到 125"""
    dates = pd.date_range(start='2024-01-01', periods=10)
    data = pd.DataFrame({
        'open': [100.0, 102.0, 104.0, 106.0, 108.0, 110.0, 112.0, 114.0, 116.0, 118.0],
        'high': [105.0, 107.0, 109.0, 111.0, 113.0, 115.0, 117.0, 119.0, 121.0, 128.0],
        'low': [99.0, 101.0, 103.0, 105.0, 107.0, 109.0, 111.0, 113.0, 115.0, 117.0],
        'close': [100.0, 102.5, 105.0, 107.5, 110.0, 112.5, 115.0, 117.5, 120.0, 125.0],
        'volume': [1000] * 10
    }, index=dates)
    return data

def test_buy_hold_return_positive(sample_data):
    """測試正報酬"""
    result = calculate_buy_hold_return(sample_data)
    
    # (125 - 100) / 100 = 0.25
    assert abs(result - 0.25) < 0.01

def test_buy_hold_return_negative():
    """測試負報酬"""
    dates = pd.date_range(start='2024-01-01', periods=5)
    data = pd.DataFrame({
        'close': [100.0, 90.0, 80.0, 70.0, 60.0]
    }, index=dates)
    
    result = calculate_buy_hold_return(data)
    
    # (60 - 100) / 100 = -0.40
    assert abs(result - (-0.40)) < 0.01

def test_buy_hold_return_empty():
    """測試空資料"""
    data = pd.DataFrame()
    result = calculate_buy_hold_return(data)
    assert result == 0.0
