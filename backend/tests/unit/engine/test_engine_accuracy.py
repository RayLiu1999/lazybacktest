
import pytest
import pandas as pd
from datetime import datetime
from app.modules.backtest.engine import BacktestEngine, BacktestConfig

@pytest.fixture
def sample_data():
    data = {
        "open": [100.0, 100.0, 100.0, 100.0, 100.0],
        "high": [105.0, 105.0, 105.0, 105.0, 105.0],
        "low": [95.0, 95.0, 95.0, 95.0, 95.0],
        "close": [100.0, 100.0, 100.0, 100.0, 100.0],
        "adj_close": [90.0, 90.0, 90.0, 90.0, 90.0], # 模擬除權息
        "volume": [1000, 1000, 1000, 1000, 1000],
        "dividends": [0.0, 0.0, 5.0, 0.0, 0.0], # Day 3 配息 5元
        "stock_splits": [0.0, 0.0, 0.0, 0.0, 0.0]
    }
    dates = pd.date_range(start="2024-01-01", periods=5)
    df = pd.DataFrame(data, index=dates)
    df.index.name = "date"
    return df

class TestEngineAccuracy:
    
    def test_slippage_buy(self):
        """測試買入滑價"""
        config = BacktestConfig(
            initial_capital=200000, 
            ticker="2330",
            slippage=0.01  # 1% 滑價
        )
        engine = BacktestEngine(config)
        
        # 買入價格 100
        engine.buy(100.0, 1000, datetime.now())
        
        # 預期實際成交價 = 100 * 1.01 = 101
        assert engine.trades[0].price == pytest.approx(101.0)
        
    def test_slippage_sell(self):
        """測試賣出滑價"""
        config = BacktestConfig(
            initial_capital=100000, 
            ticker="2330",
            slippage=0.01  # 1% 滑價
        )
        engine = BacktestEngine(config)
        
        # 先買入建立持倉
        engine.position = 1000
        engine.entry_price = 100.0
        
        # 賣出價格 100
        engine.sell(100.0, 1000, datetime.now())
        
        # 預期實際成交價 = 100 * (1 - 0.01) = 99
        assert engine.trades[0].price == pytest.approx(99.0)

    def test_min_commission(self):
        """測試最低手續費"""
        config = BacktestConfig(
            initial_capital=100000, 
            ticker="2330",
            min_commission=20.0,
            buy_fee=0.001425
        )
        engine = BacktestEngine(config)
        
        # 小額交易: 10元 * 10股 = 100元 -> 手續費 0.1425元 -> 應收 20元
        engine.buy(10.0, 10, datetime.now())
        
        assert engine.trades[0].fee == 20.0

    def test_dividend_reinvestment(self, sample_data):
        """測試股息再投入"""
        config = BacktestConfig(
            initial_capital=100000,
            ticker="2330",
            reinvest_dividends=True
        )
        engine = BacktestEngine(config)
        
        # Day 1 持有 1000 股
        engine.position = 1000
        engine.cash = 0
        
        # 執行回測 logic (簡化模擬)
        # 直接呼叫 run 會比較複雜，這裡模擬 run 中的邏輯片段
        # 但為了完整測試，我們呼叫 run
        
        # 產生假訊號 (不買不賣，只持有)
        entry_signal = pd.Series([False]*5, index=sample_data.index)
        exit_signal = pd.Series([False]*5, index=sample_data.index)
        
        engine.run(sample_data, entry_signal, exit_signal)
        
        # 檢查是否有 DIVIDEND 交易
        div_trades = [t for t in engine.trades if t.action == "DIVIDEND"]
        assert len(div_trades) == 1
        assert div_trades[0].profit == 5.0 * 1000  # 5元 * 1000股 = 5000
        assert engine.cash == 5000  # 現金增加 5000

    def test_adjusted_price_usage(self, sample_data):
        """測試是否使用還原股價"""
        config = BacktestConfig(
            initial_capital=100000,
            ticker="2330",
            use_adjusted_price=True
        )
        engine = BacktestEngine(config)
        
        # 測試 _get_price
        row = sample_data.iloc[0]
        price = engine._get_price(row, 'close')
        assert price == 90.0  # 應該是 adj_close
        
        # 測試 Open 價格調整 (Open 100, Close 100, Adj Close 90 -> Factor 0.9)
        # Open 應該被調整為 100 * 0.9 = 90
        open_price = engine._get_price(row, 'open')
        assert open_price == pytest.approx(90.0)

