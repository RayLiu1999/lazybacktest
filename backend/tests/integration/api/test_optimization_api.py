from fastapi.testclient import TestClient
from unittest.mock import Mock
import pytest
import pandas as pd
from app.main import app
from app.api.deps import get_stock_repo

client = TestClient(app)

class TestOptimizationAPI:
    @pytest.fixture
    def mock_repo(self):
        repo = Mock()
        app.dependency_overrides[get_stock_repo] = lambda: repo
        yield repo
        app.dependency_overrides.clear()

    def test_run_optimization_success(self, mock_repo):
        """測試參數優化 API 端點"""
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
            "entry_strategy": "SMA_CROSS",
            "param_ranges": {
                "short_period": [5, 10],
                "long_period": [20, 30]
            }
        }

        response = client.post("/api/v1/backtest/optimize", json=payload)
        
        # 目前應該會失敗 (404), 因為路徑還沒定義
        assert response.status_code == 200
        result = response.json()
        assert "results" in result
        assert len(result["results"]) == 4
        assert "metrics" in result["results"][0]
