"""
🔴 TDD 紅燈階段：回測引擎核心測試

測試回測引擎的基本功能：
1. 買入邏輯
2. 賣出邏輯
3. 手續費計算
4. 停損停利
5. 權益曲線計算
"""
import pytest
import pandas as pd
import numpy as np
from decimal import Decimal

from app.modules.backtest.engine import BacktestEngine, BacktestConfig, Trade, BacktestResult


class TestBacktestConfig:
    """回測配置測試"""

    def test_config_defaults(self):
        """測試預設配置"""
        config = BacktestConfig(
            initial_capital=100000,
            ticker="2330"
        )
        
        assert config.initial_capital == 100000
        assert config.ticker == "2330"
        assert config.buy_fee == 0.001425  # 預設手續費
        assert config.sell_fee == 0.001425
        assert config.tax == 0.003  # 預設證交稅

    def test_config_custom_fees(self):
        """測試自訂手續費"""
        config = BacktestConfig(
            initial_capital=100000,
            ticker="2330",
            buy_fee=0.001,
            sell_fee=0.001,
            tax=0.0015
        )
        
        assert config.buy_fee == 0.001
        assert config.sell_fee == 0.001
        assert config.tax == 0.0015


class TestBacktestEngineBuy:
    """回測引擎買入邏輯測試"""

    def test_buy_basic(self):
        """測試基本買入"""
        config = BacktestConfig(initial_capital=100000, ticker="2330")
        engine = BacktestEngine(config)
        
        # 執行買入：價格 100，買 500 股
        engine.buy(price=100.0, quantity=500, date=pd.Timestamp("2024-01-01"))
        
        # 驗證持倉
        assert engine.position == 500
        # 驗證現金減少（含手續費）
        # 成本 = 100 * 500 * (1 + 0.001425) = 50071.25
        expected_cost = 100 * 500 * (1 + config.buy_fee)
        assert engine.cash == pytest.approx(100000 - expected_cost)

    def test_buy_insufficient_funds(self):
        """測試資金不足"""
        config = BacktestConfig(initial_capital=1000, ticker="2330")
        engine = BacktestEngine(config)
        
        # 嘗試購買超過資金的股票
        with pytest.raises(ValueError, match="Insufficient funds"):
            engine.buy(price=100.0, quantity=100, date=pd.Timestamp("2024-01-01"))

    def test_buy_records_trade(self):
        """測試買入記錄交易"""
        config = BacktestConfig(initial_capital=100000, ticker="2330")
        engine = BacktestEngine(config)
        
        engine.buy(price=100.0, quantity=500, date=pd.Timestamp("2024-01-01"))
        
        assert len(engine.trades) == 1
        assert engine.trades[0].action == "BUY"
        assert engine.trades[0].price == 100.0
        assert engine.trades[0].quantity == 500


class TestBacktestEngineSell:
    """回測引擎賣出邏輯測試"""

    def test_sell_basic(self):
        """測試基本賣出"""
        config = BacktestConfig(initial_capital=100000, ticker="2330")
        engine = BacktestEngine(config)
        
        # 先買入
        engine.buy(price=100.0, quantity=500, date=pd.Timestamp("2024-01-01"))
        cash_after_buy = engine.cash
        
        # 賣出（價格上漲到 110）
        engine.sell(price=110.0, quantity=500, date=pd.Timestamp("2024-01-02"))
        
        # 驗證持倉清空
        assert engine.position == 0
        # 驗證現金增加（含手續費和證交稅）
        # 收入 = 110 * 500 * (1 - 0.001425 - 0.003) = 54756.375
        sell_proceeds = 110 * 500 * (1 - config.sell_fee - config.tax)
        assert engine.cash == pytest.approx(cash_after_buy + sell_proceeds)

    def test_sell_no_position(self):
        """測試無持倉時賣出"""
        config = BacktestConfig(initial_capital=100000, ticker="2330")
        engine = BacktestEngine(config)
        
        with pytest.raises(ValueError, match="No position"):
            engine.sell(price=100.0, quantity=500, date=pd.Timestamp("2024-01-01"))

    def test_sell_partial(self):
        """測試部分賣出"""
        config = BacktestConfig(initial_capital=100000, ticker="2330")
        engine = BacktestEngine(config)
        
        engine.buy(price=100.0, quantity=500, date=pd.Timestamp("2024-01-01"))
        engine.sell(price=110.0, quantity=300, date=pd.Timestamp("2024-01-02"))
        
        # 應剩餘 200 股
        assert engine.position == 200


class TestBacktestEngineStopLoss:
    """停損測試"""

    def test_stop_loss_triggered(self):
        """測試停損觸發"""
        config = BacktestConfig(
            initial_capital=100000,
            ticker="2330",
            stop_loss=0.05  # 5% 停損
        )
        engine = BacktestEngine(config)
        
        engine.buy(price=100.0, quantity=500, date=pd.Timestamp("2024-01-01"))
        
        # 價格下跌 6%，應觸發停損
        should_stop = engine.check_stop_loss(current_price=94.0)
        
        assert should_stop == True

    def test_stop_loss_not_triggered(self):
        """測試停損未觸發"""
        config = BacktestConfig(
            initial_capital=100000,
            ticker="2330",
            stop_loss=0.05
        )
        engine = BacktestEngine(config)
        
        engine.buy(price=100.0, quantity=500, date=pd.Timestamp("2024-01-01"))
        
        # 價格下跌 3%，不應觸發停損
        should_stop = engine.check_stop_loss(current_price=97.0)
        
        assert should_stop == False


class TestBacktestEngineTakeProfit:
    """停利測試"""

    def test_take_profit_triggered(self):
        """測試停利觸發"""
        config = BacktestConfig(
            initial_capital=100000,
            ticker="2330",
            take_profit=0.10  # 10% 停利
        )
        engine = BacktestEngine(config)
        
        engine.buy(price=100.0, quantity=500, date=pd.Timestamp("2024-01-01"))
        
        # 價格上漲 12%，應觸發停利
        should_profit = engine.check_take_profit(current_price=112.0)
        
        assert should_profit == True

    def test_take_profit_not_triggered(self):
        """測試停利未觸發"""
        config = BacktestConfig(
            initial_capital=100000,
            ticker="2330",
            take_profit=0.10
        )
        engine = BacktestEngine(config)
        
        engine.buy(price=100.0, quantity=500, date=pd.Timestamp("2024-01-01"))
        
        # 價格上漲 8%，不應觸發停利
        should_profit = engine.check_take_profit(current_price=108.0)
        
        assert should_profit == False


class TestBacktestEngineRun:
    """完整回測執行測試"""

    def test_run_simple_strategy(self):
        """測試簡單策略回測"""
        config = BacktestConfig(initial_capital=100000, ticker="2330")
        engine = BacktestEngine(config)
        
        # 準備測試數據
        data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10),
            'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'high': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            'low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
            'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'volume': [1000000] * 10
        })
        
        # 簡單訊號：第 3 天買入，第 7 天賣出
        entry_signal = pd.Series([False, False, True, False, False, False, False, False, False, False])
        exit_signal = pd.Series([False, False, False, False, False, False, True, False, False, False])
        
        result = engine.run(data, entry_signal, exit_signal)
        
        # 驗證結果
        assert isinstance(result, BacktestResult)
        assert result.total_return > 0  # 價格上漲，應有正報酬
        assert len(result.trades) == 2  # 一買一賣

    def test_run_generates_equity_curve(self):
        """測試產生權益曲線"""
        config = BacktestConfig(initial_capital=100000, ticker="2330")
        engine = BacktestEngine(config)
        
        data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5),
            'open': [100, 101, 102, 103, 104],
            'high': [101, 102, 103, 104, 105],
            'low': [99, 100, 101, 102, 103],
            'close': [100, 101, 102, 103, 104],
            'volume': [1000000] * 5
        })
        
        entry_signal = pd.Series([True, False, False, False, False])
        exit_signal = pd.Series([False, False, False, False, True])
        
        result = engine.run(data, entry_signal, exit_signal)
        
        # 權益曲線長度應與數據相同
        assert len(result.equity_curve) == len(data)
