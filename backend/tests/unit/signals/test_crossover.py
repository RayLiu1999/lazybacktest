"""
🔴 TDD 紅燈階段：均線交叉訊號測試

黃金交叉 (Golden Cross): 短均線上穿長均線 → 買入訊號
死亡交叉 (Death Cross): 短均線下穿長均線 → 賣出訊號
"""
import pytest
import pandas as pd
import numpy as np

from app.modules.backtest.signals import golden_cross, death_cross, SignalType


class TestGoldenCross:
    """黃金交叉（買入訊號）測試"""

    def test_golden_cross_basic(self):
        """測試基本黃金交叉偵測"""
        # 準備資料：短均線從下方穿越長均線
        short_ma = pd.Series([9.0, 9.5, 10.0, 10.5, 11.0])
        long_ma = pd.Series([10.0, 10.0, 10.0, 10.0, 10.0])
        
        result = golden_cross(short_ma, long_ma)
        
        # 第 3 個位置（index 2）應該觸發黃金交叉
        # 因為 short_ma 從 9.5 (< 10) 變成 10.0 (= 10)，再變成 10.5 (> 10)
        assert result.iloc[3] == True  # index 3 穿越完成

    def test_golden_cross_no_signal(self):
        """測試沒有交叉的情況"""
        # 短均線一直在長均線上方
        short_ma = pd.Series([11.0, 12.0, 13.0, 14.0, 15.0])
        long_ma = pd.Series([10.0, 10.0, 10.0, 10.0, 10.0])
        
        result = golden_cross(short_ma, long_ma)
        
        # 應該沒有任何訊號
        assert result.sum() == 0

    def test_golden_cross_multiple_signals(self):
        """測試多次交叉"""
        short_ma = pd.Series([9.0, 11.0, 9.0, 11.0, 9.0, 11.0])
        long_ma = pd.Series([10.0, 10.0, 10.0, 10.0, 10.0, 10.0])
        
        result = golden_cross(short_ma, long_ma)
        
        # 應有 3 次黃金交叉（index 1, 3, 5）
        assert result.sum() == 3

    def test_golden_cross_returns_bool_series(self):
        """測試返回值為 bool Series"""
        short_ma = pd.Series([9.0, 10.0, 11.0])
        long_ma = pd.Series([10.0, 10.0, 10.0])
        
        result = golden_cross(short_ma, long_ma)
        
        assert isinstance(result, pd.Series)
        assert result.dtype == bool


class TestDeathCross:
    """死亡交叉（賣出訊號）測試"""

    def test_death_cross_basic(self):
        """測試基本死亡交叉偵測"""
        # 短均線從上方穿越長均線向下
        short_ma = pd.Series([11.0, 10.5, 10.0, 9.5, 9.0])
        long_ma = pd.Series([10.0, 10.0, 10.0, 10.0, 10.0])
        
        result = death_cross(short_ma, long_ma)
        
        # 應該有死亡交叉發生
        assert result.iloc[3] == True

    def test_death_cross_no_signal(self):
        """測試沒有交叉的情況"""
        # 短均線一直在長均線下方
        short_ma = pd.Series([9.0, 8.0, 7.0, 6.0, 5.0])
        long_ma = pd.Series([10.0, 10.0, 10.0, 10.0, 10.0])
        
        result = death_cross(short_ma, long_ma)
        
        # 應該沒有任何訊號
        assert result.sum() == 0

    def test_death_cross_returns_bool_series(self):
        """測試返回值為 bool Series"""
        short_ma = pd.Series([11.0, 10.0, 9.0])
        long_ma = pd.Series([10.0, 10.0, 10.0])
        
        result = death_cross(short_ma, long_ma)
        
        assert isinstance(result, pd.Series)
        assert result.dtype == bool


class TestSignalType:
    """訊號類型枚舉測試"""

    def test_signal_types_exist(self):
        """測試訊號類型枚舉存在"""
        assert SignalType.BUY is not None
        assert SignalType.SELL is not None
        assert SignalType.HOLD is not None
