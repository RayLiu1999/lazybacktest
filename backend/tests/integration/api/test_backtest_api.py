"""
🔴 TDD 紅燈階段：回測 API 測試

測試 /api/v1/backtest 相關端點：
1. POST /api/v1/backtest/run - 執行回測策略
"""
from fastapi.testclient import TestClient
from unittest.mock import Mock
import pytest
import pandas as pd
from datetime import date

from app.main import app
from app.api.deps import get_stock_repo
from app.modules.backtest.engine import BacktestResult, Trade

client = TestClient(app)


class TestBacktestAPI:
    """回測 API 整合測試"""
    
    @pytest.fixture
    def mock_repo(self):
        """Mock Repo"""
        repo = Mock()
        app.dependency_overrides[get_stock_repo] = lambda: repo
        yield repo
        app.dependency_overrides.clear()


    def test_run_backtest_success(self, mock_repo):
        """測試成功執行回測"""
        # 1. Mock 股價資料
        data = {
            "open": [100.0, 102.0, 104.0, 101.0, 103.0],
            "high": [105.0, 108.0, 106.0, 102.0, 105.0],
            "low": [99.0, 101.0, 102.0, 99.0, 101.0],
            "close": [102.0, 106.0, 103.0, 100.0, 104.0],
            "volume": [1000, 2000, 1500, 1200, 1800]
        }
        index = pd.DatetimeIndex([
            "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"
        ], name="date")
        df = pd.DataFrame(data, index=index)
        mock_repo.get_stock_data.return_value = df
        
        # 2. 請求 Payload (新版 strategy_settings 格式)
        payload = {
            "ticker": "2330",
            "start_date": "2024-01-01",
            "end_date": "2024-01-05",
            "initial_capital": 100000,
            "strategy_settings": {
                "entry_strategy": "SMA_CROSS",
                "entry_params": {"short_period": 2, "long_period": 5}
            }
        }
        
        # 3. 執行請求
        response = client.post("/api/v1/backtest/run", json=payload)
        
        # 4. 驗證
        assert response.status_code == 200
        result = response.json()
        assert "total_return" in result
        assert "trades" in result
        assert "equity_curve" in result
        assert result["ticker"] == "2330"

    def test_run_backtest_no_data(self, mock_repo):
        """測試無資料情況"""
        mock_repo.get_stock_data.return_value = pd.DataFrame()
        
        payload = {
            "ticker": "2330",
            "start_date": "2024-01-01",
            "end_date": "2024-01-05",
            "strategy_settings": {
                "entry_strategy": "SMA_CROSS",
                "entry_params": {"short_period": 5, "long_period": 20}
            }
        }
        
        response = client.post("/api/v1/backtest/run", json=payload)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "No data found for backtest"
