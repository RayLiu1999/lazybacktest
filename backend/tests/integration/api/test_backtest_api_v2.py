from fastapi.testclient import TestClient
from unittest.mock import Mock
import pytest
import pandas as pd
from app.main import app
from app.api.deps import get_stock_repo

client = TestClient(app)

class TestBacktestAPIV2:
    @pytest.fixture
    def mock_repo(self):
        repo = Mock()
        app.dependency_overrides[get_stock_repo] = lambda: repo
        yield repo
        app.dependency_overrides.clear()

    def test_run_backtest_v2_success(self, mock_repo):
        """測試使用新版嵌套結構發送回測請求"""
        # Mock 資料
        data = {
            "open": [100.0] * 20,
            "high": [105.0] * 20,
            "low": [95.0] * 20,
            "close": [100.0] * 20,
            "volume": [1000] * 20
        }
        df = pd.DataFrame(data, index=pd.date_range("2024-01-01", periods=20))
        mock_repo.get_stock_data.return_value = df

        payload = {
            "ticker": "2330",
            "start_date": "2024-01-01",
            "end_date": "2024-01-20",
            "initial_capital": 100000,
            "trading_settings": {
                "timing": "N_CLOSE",
                "buy_fee": 0.001425,
                "sell_fee": 0.004425,
                "tax": 0.003
            },
            "risk_settings": {
                "position_basis": "INITIAL_CAPITAL",
                "position_pct": 100,
                "stop_loss": 5.0,
                "take_profit": 10.0
            },
            "strategy_settings": {
                "entry_strategy": "SMA_CROSS",
                "entry_params": {"short_period": 5, "long_period": 10},
                "exit_strategy": "SAME_AS_ENTRY",
                "exit_params": {}
            }
        }

        response = client.post("/api/v1/backtest/run", json=payload)
        
        # 目前應該會失敗 (422 Unprocessable Entity)，因為 Schema 還沒更新
        assert response.status_code == 200
        result = response.json()
        assert "sharpe_ratio" in result
        assert "sortino_ratio" in result

    def test_run_backtest_v2_stop_loss(self, mock_repo):
        """測試停損功能是否生效"""
        # Day 0: Setup
        # Day 1: 價格跌，短均 <= 長均
        # Day 2: 價格漲，短均 > 長均 (金叉!)
        # Day 3: 價格大跌，觸發停損
        data = {
            "open":  [100.0, 100.0, 90.0, 110.0, 80.0, 70.0],
            "high":  [101.0, 101.0, 91.0, 111.0, 81.0, 71.0],
            "low":   [99.0,  99.0,  89.0, 109.0, 79.0, 69.0],
            "close": [100.0, 100.0, 90.0, 110.0, 80.0, 75.0],
            "volume": [1000] * 6
        }
        # SMA(2) at Day 1: (100+100)/2 = 100. SMA(1)=100. 100 <= 100 (Below or Equal)
        # SMA(2) at Day 2: (100+90)/2 = 95. SMA(1)=90. 90 <= 95 (Below or Equal)
        # SMA(2) at Day 3: (90+110)/2 = 100. SMA(1)=110. 110 > 100 (Cross Above!) -> Entry @ 110
        # SMA(2) at Day 4: (110+80)/2 = 95. SMA(1)=80. 80. 觸發 2% 停損 (80 vs 110)
        df = pd.DataFrame(data, index=pd.date_range("2024-01-01", periods=6))
        mock_repo.get_stock_data.return_value = df

        payload = {
            "ticker": "2330",
            "start_date": "2024-01-01",
            "end_date": "2024-01-05",
            "risk_settings": {
                "stop_loss": 0.02 # 2% 停損
            },
            "strategy_settings": {
                "entry_strategy": "SMA_CROSS",
                "entry_params": {"short_period": 1, "long_period": 2} # 必定金叉
            }
        }
        # 修改 mock 訊號產生邏輯或直接 mock StrategyRegistry? 
        # 不，這裡會跑真實的 StrategyRegistry。對於 1, 2 均線且價格下跌，可能不會金叉。
        # 為了測試，我們手動構造資料讓它第一天金叉
        df.iloc[0, df.columns.get_loc('close')] = 110 # 第一天超高，讓均線死叉？不，我要金叉。
        # 算了，我直接 mock StrategyRegistry.get_signals 比較快，或是確保資料會觸發。
        
        response = client.post("/api/v1/backtest/run", json=payload)
        assert response.status_code == 200
        result = response.json()
        assert len(result["trades"]) > 0
        # 檢查是否有 SELL 動作且 profit 為負且接近 2%
        sell_trades = [t for t in result["trades"] if t["action"] == "SELL"]
        assert len(sell_trades) > 0
        assert sell_trades[0]["profit"] < 0

    def test_run_backtest_v2_take_profit(self, mock_repo):
        """測試停利功能是否生效"""
        # Day 2 金叉進場，Day 3 大漲觸發停利
        data = {
            "open":  [100.0, 100.0, 90.0, 110.0, 130.0, 140.0],
            "high":  [101.0, 101.0, 91.0, 111.0, 131.0, 141.0],
            "low":   [99.0,  99.0,  89.0, 109.0, 129.0, 139.0],
            "close": [100.0, 100.0, 90.0, 110.0, 130.0, 140.0],
            "volume": [1000] * 6
        }
        df = pd.DataFrame(data, index=pd.date_range("2024-01-01", periods=6))
        mock_repo.get_stock_data.return_value = df

        payload = {
            "ticker": "2330",
            "start_date": "2024-01-01",
            "end_date": "2024-01-06",
            "risk_settings": {
                "take_profit": 0.05 # 5% 停利
            },
            "strategy_settings": {
                "entry_strategy": "SMA_CROSS",
                "entry_params": {"short_period": 1, "long_period": 2}
            }
        }
        # Day 3 (Entry @ 110)
        # Day 4 (Price @ 130) -> 130/110 = 1.18. 觸發 5% 停利
        
        response = client.post("/api/v1/backtest/run", json=payload)
        assert response.status_code == 200
        result = response.json()
        assert len(result["trades"]) > 0
        sell_trades = [t for t in result["trades"] if t["action"] == "SELL"]
        assert len(sell_trades) > 0
        assert sell_trades[0]["profit"] > 0
