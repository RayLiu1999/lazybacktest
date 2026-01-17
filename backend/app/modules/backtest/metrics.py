"""
績效指標計算模組

提供各種回測績效指標的計算函數：
- 總報酬率
- CAGR (年化報酬率)
- 最大回撤 (MDD)
- 勝率
- 索提諾比率
- 夏普比率
"""
import pandas as pd
import numpy as np
from typing import Union


def calculate_total_return(initial_value: float, final_value: float) -> float:
    """
    計算總報酬率
    
    公式: (終值 - 初值) / 初值
    
    Args:
        initial_value: 初始資金
        final_value: 最終資金
        
    Returns:
        float: 總報酬率 (小數形式，如 0.20 表示 20%)
    """
    return (final_value - initial_value) / initial_value


def calculate_cagr(initial_value: float, final_value: float, years: float) -> float:
    """
    計算年化報酬率 (Compound Annual Growth Rate)
    
    公式: (終值/初值)^(1/年數) - 1
    
    Args:
        initial_value: 初始資金
        final_value: 最終資金
        years: 投資年數
        
    Returns:
        float: 年化報酬率 (小數形式)
    """
    if years <= 0:
        return 0.0
    
    return (final_value / initial_value) ** (1 / years) - 1


def calculate_max_drawdown(equity_curve: pd.Series) -> float:
    """
    計算最大回撤 (Maximum Drawdown)
    
    最大回撤 = 從最高點到最低點的最大跌幅
    
    公式: max((累積最高值 - 當前值) / 累積最高值)
    
    Args:
        equity_curve: 權益曲線
        
    Returns:
        float: 最大回撤比例 (正數，如 0.20 表示 20% 回撤)
    """
    cummax = equity_curve.cummax()
    drawdown = (cummax - equity_curve) / cummax
    
    return drawdown.max()


def calculate_win_rate(profits: list[float]) -> float:
    """
    計算勝率
    
    公式: 獲利交易次數 / 總交易次數
    
    Args:
        profits: 每筆交易的獲利列表
        
    Returns:
        float: 勝率 (0-1)
    """
    if not profits:
        return 0.0
    
    wins = sum(1 for p in profits if p > 0)
    
    return wins / len(profits)


def calculate_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    annualization_factor: int = 252
) -> float:
    """
    計算索提諾比率 (Sortino Ratio)
    
    與夏普比率類似，但只考慮下行風險（負報酬的波動）
    
    公式: (平均報酬 - 無風險利率) / 下行標準差
    
    Args:
        returns: 日報酬率序列
        risk_free_rate: 無風險利率 (日化)
        annualization_factor: 年化因子 (預設 252 交易日)
        
    Returns:
        float: 索提諾比率
    """
    excess_returns = returns - risk_free_rate
    mean_excess = excess_returns.mean()
    
    # 計算下行標準差（只考慮負報酬）
    downside_returns = returns[returns < 0]
    
    if len(downside_returns) == 0:
        # 無下行風險，返回無窮大
        return np.inf
    
    downside_std = downside_returns.std()
    
    if downside_std == 0:
        return np.inf
    
    # 年化
    sortino = (mean_excess / downside_std) * np.sqrt(annualization_factor)
    
    return sortino


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    annualization_factor: int = 252
) -> float:
    """
    計算夏普比率 (Sharpe Ratio)
    
    衡量每承擔一單位風險所獲得的超額報酬
    
    公式: (平均報酬 - 無風險利率) / 報酬標準差
    
    Args:
        returns: 日報酬率序列
        risk_free_rate: 無風險利率 (日化)
        annualization_factor: 年化因子 (預設 252 交易日)
        
    Returns:
        float: 夏普比率
    """
    excess_returns = returns - risk_free_rate
    mean_excess = excess_returns.mean()
    std = excess_returns.std()
    
    if std == 0:
        return 0.0
    
    # 年化
    sharpe = (mean_excess / std) * np.sqrt(annualization_factor)
    
    return sharpe


def calculate_profit_factor(profits: list[float]) -> float:
    """
    計算獲利因子
    
    公式: 總獲利 / 總虧損
    
    Args:
        profits: 每筆交易的獲利列表
        
    Returns:
        float: 獲利因子
    """
    gross_profit = sum(p for p in profits if p > 0)
    gross_loss = abs(sum(p for p in profits if p < 0))
    
    if gross_loss == 0:
        return np.inf if gross_profit > 0 else 0.0
    
    return gross_profit / gross_loss


def calculate_average_trade(profits: list[float]) -> float:
    """
    計算平均每筆交易獲利
    
    Args:
        profits: 每筆交易的獲利列表
        
    Returns:
        float: 平均獲利
    """
    if not profits:
        return 0.0
    
    return sum(profits) / len(profits)


def calculate_yearly_returns(equity_curve: pd.Series) -> dict[int, float]:
    """
    計算年度報酬率
    
    Args:
        equity_curve: 權益曲線 (index 為 datetime)
        
    Returns:
        dict[int, float]: {年份: 報酬率}
    """
    if equity_curve.empty:
        return {}
    
    result = {}
    years = equity_curve.index.to_series().dt.year.unique()
    
    for year in years:
        year_data = equity_curve[equity_curve.index.year == year]
        if len(year_data) >= 2:
            start_val = year_data.iloc[0]
            end_val = year_data.iloc[-1]
            result[int(year)] = (end_val - start_val) / start_val
    
    return result


def calculate_monthly_returns(equity_curve: pd.Series) -> list[dict]:
    """
    計算月度報酬率
    
    Args:
        equity_curve: 權益曲線 (index 為 datetime)
        
    Returns:
        list[dict]: [{"year": 2024, "month": 1, "return": 0.05}, ...]
    """
    if equity_curve.empty:
        return []
    
    result = []
    
    # 按年月分組
    grouped = equity_curve.groupby([
        equity_curve.index.year,
        equity_curve.index.month
    ])
    
    for (year, month), group in grouped:
        if len(group) >= 2:
            start_val = group.iloc[0]
            end_val = group.iloc[-1]
            monthly_return = (end_val - start_val) / start_val
            result.append({
                "year": int(year),
                "month": int(month),
                "return": float(monthly_return)
            })
    
    return result


def calculate_buy_hold_return(data: pd.DataFrame) -> float:
    """
    計算買入持有報酬率
    
    Args:
        data: 股價數據 (需包含 close 欄位)
        
    Returns:
        float: 買入持有報酬率
    """
    if data.empty or len(data) < 2:
        return 0.0
    
    return (data['close'].iloc[-1] / data['close'].iloc[0]) - 1
