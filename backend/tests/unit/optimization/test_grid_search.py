import pytest
import pandas as pd
import numpy as np
from app.modules.backtest.optimization import grid_search
from app.modules.backtest.strategies import StrategyRegistry

@pytest.fixture
def sample_data():
    dates = pd.date_range(start='2024-01-01', periods=100)
    data = pd.DataFrame({
        'open': np.linspace(100, 110, 100),
        'high': np.linspace(105, 115, 100),
        'low': np.linspace(95, 105, 100),
        'close': np.linspace(100, 110, 100),
        'volume': np.random.randint(1000, 5000, 100)
    }, index=dates)
    return data

def test_grid_search_sma_cross(sample_data):
    """測試 SMA_CROSS 的參數窮舉"""
    param_ranges = {
        "short_period": [5, 10],
        "long_period": [20, 30]
    }
    # 組合應該有 2 * 2 = 4 種
    results = grid_search("SMA_CROSS", param_ranges, sample_data, initial_capital=100000)
    
    assert len(results) == 4
    # 檢查結果結構
    first_result = results[0]
    assert "params" in first_result
    assert "metrics" in first_result
    assert "short_period" in first_result["params"]
    assert "total_return" in first_result["metrics"]
    assert "sharpe_ratio" in first_result["metrics"]

def test_grid_search_sorting(sample_data):
    """測試結果是否按績效排序 (預設 Sharpe Ratio)"""
    param_ranges = {
        "short_period": [5, 10],
        "long_period": [20, 30]
    }
    results = grid_search("SMA_CROSS", param_ranges, sample_data)
    
    # 檢查是否降序
    sharpes = [r["metrics"]["sharpe_ratio"] for r in results]
    assert sharpes == sorted(sharpes, reverse=True)

def test_grid_search_invalid_strategy(sample_data):
    """測試無效策略"""
    with pytest.raises(ValueError):
        grid_search("INVALID", {}, sample_data)
