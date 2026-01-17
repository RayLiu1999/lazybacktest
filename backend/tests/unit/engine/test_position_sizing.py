"""
TDD 測試: 倉位比例控制
- position_pct: 單次投入比例 (0-100%)
- position_basis: 計算基準 (INITIAL_CAPITAL / TOTAL_CAPITAL)
"""
import pytest
import pandas as pd
from app.modules.backtest.engine import BacktestEngine, BacktestConfig

@pytest.fixture
def sample_data():
    """10 天測試資料"""
    dates = pd.date_range(start='2024-01-01', periods=10)
    data = pd.DataFrame({
        'open': [100.0] * 10,
        'high': [105.0] * 10,
        'low': [95.0] * 10,
        'close': [100.0] * 10,
        'volume': [1000] * 10
    }, index=dates)
    return data

def test_position_50_pct(sample_data):
    """測試 50% 倉位"""
    config = BacktestConfig(
        initial_capital=100000,
        ticker="TEST",
        position_pct=50.0  # 只用 50% 資金
    )
    engine = BacktestEngine(config)
    
    # Day 0 觸發進場
    entry_signal = pd.Series([True] + [False] * 9, index=sample_data.index)
    exit_signal = pd.Series([False] * 10, index=sample_data.index)
    
    result = engine.run(sample_data, entry_signal, exit_signal)
    
    # 應該只買 50000 / 100 = 500 股 (調整為整百)
    assert len(result.trades) >= 1
    buy_trade = result.trades[0]
    # 50000 / (100 * 1.001425) ≈ 499.3 → 調整為 400 股
    assert buy_trade.quantity <= 500

def test_position_basis_total_capital(sample_data):
    """測試以總資金為基準"""
    # 模擬資金成長的情境
    config = BacktestConfig(
        initial_capital=100000,
        ticker="TEST",
        position_pct=100.0,
        position_basis="TOTAL_CAPITAL"  # 以總資金為基準
    )
    engine = BacktestEngine(config)
    
    entry_signal = pd.Series([True] + [False] * 9, index=sample_data.index)
    exit_signal = pd.Series([False] * 10, index=sample_data.index)
    
    result = engine.run(sample_data, entry_signal, exit_signal)
    
    # 基本驗證：應該有交易
    assert len(result.trades) >= 1

def test_position_basis_initial_capital(sample_data):
    """測試以初始資金為基準 (預設)"""
    config = BacktestConfig(
        initial_capital=100000,
        ticker="TEST",
        position_pct=100.0,
        position_basis="INITIAL_CAPITAL"
    )
    engine = BacktestEngine(config)
    
    entry_signal = pd.Series([True] + [False] * 9, index=sample_data.index)
    exit_signal = pd.Series([False] * 10, index=sample_data.index)
    
    result = engine.run(sample_data, entry_signal, exit_signal)
    
    assert len(result.trades) >= 1
    # 100% 的 100000 = 100000
    # 100000 / (100 * 1.001425) ≈ 998.6 → 900 股
    assert result.trades[0].quantity == 900
