"""
🔴 TDD 紅燈階段：RSI (相對強弱指標) 測試

RSI = 100 - (100 / (1 + RS))
RS = 平均漲幅 / 平均跌幅

範圍：0-100
- > 70: 超買區
- < 30: 超賣區
"""
import pytest
import pandas as pd
import numpy as np

from app.modules.backtest.indicators import rsi


class TestRSI:
    """RSI 相對強弱指標測試"""

    def test_rsi_basic_calculation(self):
        """測試基本 RSI 計算"""
        # 準備持續上漲的價格（應該接近 100）
        prices = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0])
        period = 5

        result = rsi(prices, period)

        # 持續上漲，RSI 應該接近 100
        assert result.iloc[-1] > 90

    def test_rsi_downtrend(self):
        """測試持續下跌的 RSI（應接近 0）"""
        prices = pd.Series([20.0, 19.0, 18.0, 17.0, 16.0, 15.0, 14.0, 13.0, 12.0, 11.0, 10.0])
        period = 5

        result = rsi(prices, period)

        # 持續下跌，RSI 應該接近 0
        assert result.iloc[-1] < 10

    def test_rsi_range(self):
        """測試 RSI 值在 0-100 範圍內"""
        # 混合漲跌的價格
        prices = pd.Series([10.0, 12.0, 11.0, 13.0, 12.0, 14.0, 13.0, 15.0, 14.0, 16.0])
        period = 5

        result = rsi(prices, period)

        # 過濾掉 NaN 值
        valid_values = result.dropna()
        
        # 所有值都應在 0-100 範圍內
        assert (valid_values >= 0).all()
        assert (valid_values <= 100).all()

    def test_rsi_default_period(self):
        """測試預設週期 14"""
        prices = pd.Series(list(range(1, 30)))  # 1 到 29

        result = rsi(prices)  # 使用預設 period=14

        # 結果長度應與輸入相同
        assert len(result) == len(prices)

    def test_rsi_insufficient_data(self):
        """測試資料不足情況"""
        prices = pd.Series([10.0, 11.0, 12.0])
        period = 5

        result = rsi(prices, period)

        # 資料只有 3 筆，期間是 5，所有值都應為 NaN
        assert result.isna().all()

    def test_rsi_invalid_period(self):
        """測試無效週期"""
        prices = pd.Series([10.0, 11.0, 12.0])

        with pytest.raises(ValueError):
            rsi(prices, 0)

        with pytest.raises(ValueError):
            rsi(prices, -1)

    def test_rsi_flat_prices(self):
        """測試價格完全不變的情況"""
        prices = pd.Series([10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0])
        period = 3

        result = rsi(prices, period)

        # 價格不變，RSI 應為 NaN (0/0 情況)
        # 或者某些實作會返回 50
        valid_values = result.dropna()
        if len(valid_values) > 0:
            # 如果有值，應該是 NaN 或接近中間值
            assert valid_values.isna().all() or (valid_values == 50).any() or np.isnan(valid_values.iloc[-1])
