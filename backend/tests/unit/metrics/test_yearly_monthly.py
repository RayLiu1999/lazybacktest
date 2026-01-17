"""
TDD 測試: 年度/月度報酬分析
- calculate_yearly_returns: 每年報酬率
- calculate_monthly_returns: 每月報酬率
"""
import pytest
import pandas as pd
import numpy as np
from app.modules.backtest.metrics import calculate_yearly_returns, calculate_monthly_returns

@pytest.fixture
def equity_curve_2_years():
    """模擬 2 年的權益曲線"""
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='B')
    # 模擬從 100000 成長到 120000 的權益曲線
    values = np.linspace(100000, 120000, len(dates))
    return pd.Series(values, index=dates)

def test_yearly_returns_basic(equity_curve_2_years):
    """測試年度報酬計算"""
    result = calculate_yearly_returns(equity_curve_2_years)
    
    # 應該有 2023 和 2024 兩年
    assert 2023 in result
    assert 2024 in result
    
    # 每年應該有正報酬
    assert result[2023] > 0
    assert result[2024] > 0

def test_yearly_returns_dict_format(equity_curve_2_years):
    """測試返回格式為 dict"""
    result = calculate_yearly_returns(equity_curve_2_years)
    
    assert isinstance(result, dict)
    # 值應該是 float
    for year, ret in result.items():
        assert isinstance(year, int)
        assert isinstance(ret, float)

def test_monthly_returns_basic(equity_curve_2_years):
    """測試月度報酬計算"""
    result = calculate_monthly_returns(equity_curve_2_years)
    
    # 應該回傳 list of dict
    assert isinstance(result, list)
    assert len(result) > 0
    
    # 每個元素應該有 year, month, return
    first = result[0]
    assert 'year' in first
    assert 'month' in first
    assert 'return' in first

def test_monthly_returns_all_months(equity_curve_2_years):
    """測試覆蓋所有月份"""
    result = calculate_monthly_returns(equity_curve_2_years)
    
    # 應該有 24 個月 (2023-01 到 2024-12)
    assert len(result) >= 20  # 至少有 20 個月 (排除首月)
