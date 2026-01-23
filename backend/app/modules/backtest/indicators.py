"""
技術指標計算模組

提供各種技術分析指標的計算函數：
- SMA: 簡單移動平均
- EMA: 指數移動平均
- RSI: 相對強弱指標
- MACD: 指數平滑異同移動平均
- KD: 隨機指標
- Bollinger Bands: 布林通道
"""
import pandas as pd
import numpy as np


def sma(prices: pd.Series, period: int) -> pd.Series:
    """
    計算簡單移動平均 (Simple Moving Average)
    
    SMA = (P1 + P2 + ... + Pn) / n
    
    Args:
        prices: 價格序列 (通常是收盤價)
        period: 計算週期 (天數)
        
    Returns:
        pd.Series: SMA 序列，前 (period-1) 個值為 NaN
        
    Raises:
        ValueError: 當 period <= 0 時拋出
        
    Example:
        >>> prices = pd.Series([10, 11, 12, 13, 14])
        >>> sma(prices, 3)
        0     NaN
        1     NaN
        2    11.0
        3    12.0
        4    13.0
        dtype: float64
    """
    if period <= 0:
        raise ValueError(f"Period must be positive, got {period}")
    
    return prices.rolling(window=period).mean()


def ema(prices: pd.Series, period: int) -> pd.Series:
    """
    計算指數移動平均 (Exponential Moving Average)
    
    EMA 更重視近期價格，反應更靈敏
    
    Args:
        prices: 價格序列
        period: 計算週期
        
    Returns:
        pd.Series: EMA 序列
    """
    if period <= 0:
        raise ValueError(f"Period must be positive, got {period}")
    
    return prices.ewm(span=period, adjust=False).mean()


def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    計算相對強弱指標 (Relative Strength Index)
    
    RSI = 100 - (100 / (1 + RS))
    RS = 平均漲幅 / 平均跌幅
    
    Args:
        prices: 價格序列
        period: 計算週期 (預設 14)
        
    Returns:
        pd.Series: RSI 序列 (0-100)
    """
    if period <= 0:
        raise ValueError(f"Period must be positive, got {period}")
    
    delta = prices.diff()
    
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta.where(delta < 0, 0.0))
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    rsi_values = 100 - (100 / (1 + rs))
    
    return rsi_values


def macd(
    prices: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    計算 MACD 指標
    
    DIF = 快線 EMA - 慢線 EMA
    MACD Signal = DIF 的 EMA
    Histogram = DIF - MACD Signal
    
    Args:
        prices: 價格序列
        fast_period: 快線週期 (預設 12)
        slow_period: 慢線週期 (預設 26)
        signal_period: 訊號線週期 (預設 9)
        
    Returns:
        tuple: (DIF, MACD Signal, Histogram)
    """
    ema_fast = ema(prices, fast_period)
    ema_slow = ema(prices, slow_period)
    
    dif = ema_fast - ema_slow
    macd_signal = ema(dif, signal_period)
    histogram = dif - macd_signal
    
    return dif, macd_signal, histogram


def kd(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 9,
    k_smooth: int = 3,
    d_smooth: int = 3
) -> tuple[pd.Series, pd.Series]:
    """
    計算 KD 隨機指標
    
    RSV = (收盤價 - N日最低) / (N日最高 - N日最低) × 100
    K = RSV 的移動平均
    D = K 的移動平均
    
    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        period: RSV 計算週期 (預設 9)
        k_smooth: K 值平滑週期 (預設 3)
        d_smooth: D 值平滑週期 (預設 3)
        
    Returns:
        tuple: (K, D)
    """
    lowest_low = low.rolling(window=period).min()
    highest_high = high.rolling(window=period).max()
    
    rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
    
    k_value = rsv.rolling(window=k_smooth).mean()
    d_value = k_value.rolling(window=d_smooth).mean()
    
    return k_value, d_value


def bollinger_bands(
    prices: pd.Series,
    period: int = 20,
    std_dev: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    計算布林通道
    
    中軌 = SMA
    上軌 = SMA + (標準差 × 倍數)
    下軌 = SMA - (標準差 × 倍數)
    
    Args:
        prices: 價格序列
        period: 計算週期 (預設 20)
        std_dev: 標準差倍數 (預設 2.0)
        
    Returns:
        tuple: (上軌, 中軌, 下軌)
    """
    middle_band = sma(prices, period)
    std = prices.rolling(window=period).std()
    
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    return upper_band, middle_band, lower_band


def turtle_channel(
    high: pd.Series,
    low: pd.Series,
    period: int = 20
) -> tuple[pd.Series, pd.Series]:
    """
    計算海龜通道（唐奇安通道）
    
    海龜交易法則使用的通道指標：
    - 上軌 = 過去 N 日最高價
    - 下軌 = 過去 N 日最低價
    
    Args:
        high: 最高價序列
        low: 最低價序列
        period: 計算週期 (預設 20)
        
    Returns:
        tuple: (上軌, 下軌)
        
    Example:
        >>> entry_channel = turtle_channel(high, low, 20)
        >>> exit_channel = turtle_channel(high, low, 10)
    """
    if period <= 0:
        raise ValueError(f"Period must be positive, got {period}")
    
    upper = high.rolling(window=period).max()
    lower = low.rolling(window=period).min()
    
    return upper, lower

