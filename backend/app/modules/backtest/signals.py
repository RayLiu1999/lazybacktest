"""
交易訊號產生器模組

提供各種進場/出場訊號的計算函數：
- 均線交叉（黃金交叉、死亡交叉）
- RSI 超買超賣
- 價格突破
- MACD 交叉
"""
import pandas as pd
import numpy as np
from enum import Enum


class SignalType(Enum):
    """交易訊號類型"""
    BUY = "buy"      # 買入訊號
    SELL = "sell"    # 賣出訊號
    HOLD = "hold"    # 持有/觀望


def golden_cross(short_ma: pd.Series, long_ma: pd.Series) -> pd.Series:
    """
    偵測黃金交叉（Golden Cross）
    
    當短均線從下方穿越長均線向上時，產生買入訊號。
    
    Args:
        short_ma: 短期移動平均線
        long_ma: 長期移動平均線
        
    Returns:
        pd.Series[bool]: 黃金交叉發生的位置為 True
        
    Example:
        >>> short = pd.Series([9, 10, 11])
        >>> long = pd.Series([10, 10, 10])
        >>> golden_cross(short, long)
        0    False
        1    False
        2     True
        dtype: bool
    """
    # 前一時刻：短均線 <= 長均線
    prev_below_or_equal = short_ma.shift(1) <= long_ma.shift(1)
    
    # 當前時刻：短均線 > 長均線
    curr_above = short_ma > long_ma
    
    # 黃金交叉 = 從下方穿越到上方
    return (prev_below_or_equal & curr_above).fillna(False)


def death_cross(short_ma: pd.Series, long_ma: pd.Series) -> pd.Series:
    """
    偵測死亡交叉（Death Cross）
    
    當短均線從上方穿越長均線向下時，產生賣出訊號。
    
    Args:
        short_ma: 短期移動平均線
        long_ma: 長期移動平均線
        
    Returns:
        pd.Series[bool]: 死亡交叉發生的位置為 True
    """
    # 前一時刻：短均線 >= 長均線
    prev_above_or_equal = short_ma.shift(1) >= long_ma.shift(1)
    
    # 當前時刻：短均線 < 長均線
    curr_below = short_ma < long_ma
    
    # 死亡交叉 = 從上方穿越到下方
    return (prev_above_or_equal & curr_below).fillna(False)


def rsi_oversold(rsi_values: pd.Series, threshold: float = 30.0) -> pd.Series:
    """
    偵測 RSI 超賣訊號
    
    當 RSI 低於閾值時，視為超賣，可能是買入時機。
    
    Args:
        rsi_values: RSI 值序列
        threshold: 超賣閾值（預設 30）
        
    Returns:
        pd.Series[bool]: 超賣的位置為 True
    """
    return rsi_values < threshold


def rsi_overbought(rsi_values: pd.Series, threshold: float = 70.0) -> pd.Series:
    """
    偵測 RSI 超買訊號
    
    當 RSI 高於閾值時，視為超買，可能是賣出時機。
    
    Args:
        rsi_values: RSI 值序列
        threshold: 超買閾值（預設 70）
        
    Returns:
        pd.Series[bool]: 超買的位置為 True
    """
    return rsi_values > threshold


def price_breakout_high(
    close: pd.Series,
    high: pd.Series,
    period: int = 20
) -> pd.Series:
    """
    偵測價格向上突破訊號
    
    當收盤價突破過去 N 日最高價時，產生買入訊號。
    
    Args:
        close: 收盤價序列
        high: 最高價序列
        period: 回顧期間
        
    Returns:
        pd.Series[bool]: 突破位置為 True
    """
    highest = high.rolling(window=period).max().shift(1)
    return close > highest


def price_breakout_low(
    close: pd.Series,
    low: pd.Series,
    period: int = 20
) -> pd.Series:
    """
    偵測價格向下突破訊號
    
    當收盤價跌破過去 N 日最低價時，產生賣出訊號。
    
    Args:
        close: 收盤價序列
        low: 最低價序列
        period: 回顧期間
        
    Returns:
        pd.Series[bool]: 突破位置為 True
    """
    lowest = low.rolling(window=period).min().shift(1)
    return close < lowest


def macd_cross_up(dif: pd.Series, macd_signal: pd.Series) -> pd.Series:
    """
    偵測 MACD 金叉
    
    當 DIF 從下方穿越 MACD 訊號線時，產生買入訊號。
    
    Args:
        dif: DIF 線（快線減慢線）
        macd_signal: MACD 訊號線
        
    Returns:
        pd.Series[bool]: 金叉位置為 True
    """
    return golden_cross(dif, macd_signal)


def macd_cross_down(dif: pd.Series, macd_signal: pd.Series) -> pd.Series:
    """
    偵測 MACD 死叉
    
    當 DIF 從上方穿越 MACD 訊號線時，產生賣出訊號。
    
    Args:
        dif: DIF 線
        macd_signal: MACD 訊號線
        
    Returns:
        pd.Series[bool]: 死叉位置為 True
    """
    return death_cross(dif, macd_signal)
