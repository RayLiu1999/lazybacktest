"""
🔴 TDD 紅燈階段：SMA (簡單移動平均) 測試

測試案例：
1. 基本 SMA 計算
2. 邊界情況：資料不足
3. 邊界情況：週期為 1
"""
import pytest
import pandas as pd
import numpy as np

from app.modules.backtest.indicators import sma


class TestSMA:
    """SMA 簡單移動平均測試"""

    def test_sma_basic_calculation(self):
        """測試基本 SMA 計算 - 5 日均線"""
        # Arrange: 準備測試資料
        prices = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0])
        period = 5

        # Act: 執行計算
        result = sma(prices, period)

        # Assert: 驗證結果
        # 前 4 個值應為 NaN (資料不足)
        assert pd.isna(result.iloc[0])
        assert pd.isna(result.iloc[3])
        
        # 第 5 個值 = (10+11+12+13+14) / 5 = 12.0
        assert result.iloc[4] == pytest.approx(12.0)
        
        # 第 6 個值 = (11+12+13+14+15) / 5 = 13.0
        assert result.iloc[5] == pytest.approx(13.0)
        
        # 第 7 個值 = (12+13+14+15+16) / 5 = 14.0
        assert result.iloc[6] == pytest.approx(14.0)

    def test_sma_insufficient_data(self):
        """測試資料不足情況 - 資料筆數少於週期"""
        prices = pd.Series([10.0, 11.0, 12.0])
        period = 5

        result = sma(prices, period)

        # 所有值都應為 NaN
        assert result.isna().all()

    def test_sma_period_one(self):
        """測試週期為 1 的情況 - 應返回原始值"""
        prices = pd.Series([10.0, 20.0, 30.0])
        period = 1

        result = sma(prices, period)

        # 應該與原始價格相同
        pd.testing.assert_series_equal(result, prices)

    def test_sma_with_decimal_values(self):
        """測試帶小數的價格"""
        prices = pd.Series([10.5, 11.3, 12.7, 13.2, 14.8])
        period = 3

        result = sma(prices, period)

        # 第 3 個值 = (10.5+11.3+12.7) / 3 = 11.5
        assert result.iloc[2] == pytest.approx(11.5)
        
        # 第 4 個值 = (11.3+12.7+13.2) / 3 = 12.4
        assert result.iloc[3] == pytest.approx(12.4)

    def test_sma_empty_series(self):
        """測試空序列"""
        prices = pd.Series([], dtype=float)
        period = 5

        result = sma(prices, period)

        assert len(result) == 0

    def test_sma_invalid_period(self):
        """測試無效週期 - 應拋出異常"""
        prices = pd.Series([10.0, 11.0, 12.0])

        with pytest.raises(ValueError):
            sma(prices, 0)

        with pytest.raises(ValueError):
            sma(prices, -1)
