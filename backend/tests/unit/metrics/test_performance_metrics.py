"""
🔴 TDD 紅燈階段：績效指標測試

測試各種回測績效指標的計算：
1. 總報酬率
2. CAGR (年化報酬率)
3. 最大回撤 (MDD)
4. 勝率
5. 索提諾比率
"""
import pytest
import pandas as pd
import numpy as np

from app.modules.backtest.metrics import (
    calculate_total_return,
    calculate_cagr,
    calculate_max_drawdown,
    calculate_win_rate,
    calculate_sortino_ratio,
    calculate_sharpe_ratio
)


class TestTotalReturn:
    """總報酬率測試"""

    def test_total_return_positive(self):
        """測試正報酬"""
        initial = 100000
        final = 120000
        
        result = calculate_total_return(initial, final)
        
        assert result == pytest.approx(0.20)  # 20%

    def test_total_return_negative(self):
        """測試負報酬"""
        initial = 100000
        final = 80000
        
        result = calculate_total_return(initial, final)
        
        assert result == pytest.approx(-0.20)  # -20%

    def test_total_return_zero(self):
        """測試零報酬"""
        initial = 100000
        final = 100000
        
        result = calculate_total_return(initial, final)
        
        assert result == pytest.approx(0.0)


class TestCAGR:
    """年化報酬率測試"""

    def test_cagr_one_year(self):
        """測試一年期 CAGR"""
        initial = 100000
        final = 120000
        years = 1.0
        
        result = calculate_cagr(initial, final, years)
        
        # 一年 20% 報酬，CAGR = 20%
        assert result == pytest.approx(0.20)

    def test_cagr_two_years(self):
        """測試兩年期 CAGR"""
        initial = 100000
        final = 121000
        years = 2.0
        
        result = calculate_cagr(initial, final, years)
        
        # 兩年 21% 報酬，CAGR ≈ 10%
        assert result == pytest.approx(0.10, rel=0.01)

    def test_cagr_negative_return(self):
        """測試負報酬 CAGR"""
        initial = 100000
        final = 81000
        years = 2.0
        
        result = calculate_cagr(initial, final, years)
        
        # 兩年虧損 19%，CAGR ≈ -10%
        assert result == pytest.approx(-0.10, rel=0.01)


class TestMaxDrawdown:
    """最大回撤測試"""

    def test_mdd_basic(self):
        """測試基本最大回撤計算"""
        # 從 100 漲到 120，再跌到 96
        equity_curve = pd.Series([100, 110, 120, 108, 96, 100, 110])
        
        result = calculate_max_drawdown(equity_curve)
        
        # MDD = (120 - 96) / 120 = 20%
        assert result == pytest.approx(0.20)

    def test_mdd_no_drawdown(self):
        """測試無回撤情況（持續上漲）"""
        equity_curve = pd.Series([100, 110, 120, 130, 140])
        
        result = calculate_max_drawdown(equity_curve)
        
        assert result == pytest.approx(0.0)

    def test_mdd_continuous_decline(self):
        """測試持續下跌"""
        equity_curve = pd.Series([100, 90, 80, 70, 60])
        
        result = calculate_max_drawdown(equity_curve)
        
        # MDD = (100 - 60) / 100 = 40%
        assert result == pytest.approx(0.40)


class TestWinRate:
    """勝率測試"""

    def test_win_rate_all_wins(self):
        """測試全部獲利"""
        profits = [100, 200, 300, 400]
        
        result = calculate_win_rate(profits)
        
        assert result == pytest.approx(1.0)

    def test_win_rate_all_losses(self):
        """測試全部虧損"""
        profits = [-100, -200, -300, -400]
        
        result = calculate_win_rate(profits)
        
        assert result == pytest.approx(0.0)

    def test_win_rate_mixed(self):
        """測試混合勝敗"""
        profits = [100, -50, 200, -100]
        
        result = calculate_win_rate(profits)
        
        # 2 勝 / 4 總 = 50%
        assert result == pytest.approx(0.5)

    def test_win_rate_empty(self):
        """測試無交易"""
        profits = []
        
        result = calculate_win_rate(profits)
        
        assert result == pytest.approx(0.0)


class TestSortinoRatio:
    """索提諾比率測試"""

    def test_sortino_basic(self):
        """測試基本索提諾比率計算"""
        # 模擬日報酬率
        returns = pd.Series([0.01, 0.02, -0.01, 0.015, -0.005, 0.01, 0.02])
        risk_free_rate = 0.0
        
        result = calculate_sortino_ratio(returns, risk_free_rate)
        
        # 正報酬為主，索提諾比率應為正值
        assert result > 0

    def test_sortino_no_downside(self):
        """測試無下行風險"""
        # 全部正報酬
        returns = pd.Series([0.01, 0.02, 0.015, 0.01, 0.02])
        risk_free_rate = 0.0
        
        result = calculate_sortino_ratio(returns, risk_free_rate)
        
        # 無下行風險，比率趨近無窮大（返回 inf 或很大的值）
        assert result > 10 or np.isinf(result)


class TestSharpeRatio:
    """夏普比率測試"""

    def test_sharpe_basic(self):
        """測試基本夏普比率計算"""
        returns = pd.Series([0.01, 0.02, -0.01, 0.015, -0.005, 0.01, 0.02])
        risk_free_rate = 0.0
        
        result = calculate_sharpe_ratio(returns, risk_free_rate)
        
        # 正平均報酬，夏普比率應為正值
        assert result > 0

    def test_sharpe_negative(self):
        """測試負夏普比率"""
        returns = pd.Series([-0.01, -0.02, -0.01, -0.015, -0.005])
        risk_free_rate = 0.0
        
        result = calculate_sharpe_ratio(returns, risk_free_rate)
        
        # 負平均報酬，夏普比率應為負值
        assert result < 0
