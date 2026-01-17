"""
🔴 TDD 紅燈階段：股票資料 API 測試

測試 /api/v1/stocks 相關端點：
1. GET /api/v1/stocks/{ticker}/history - 取得歷史股價
"""
from fastapi.testclient import TestClient
from unittest.mock import Mock
from datetime import date
import pandas as pd
import pytest

from app.main import app
from app.api.deps import get_stock_repo
# from app.api.v1.endpoints import stocks  # 預期尚未建立

client = TestClient(app)


class TestStocksAPI:
    """股票 API 整合測試"""
    
    @pytest.fixture
    def mock_repo(self):
        """Mock Repository Dependency using dependency_overrides"""
        repo = Mock()
        app.dependency_overrides[get_stock_repo] = lambda: repo
        yield repo
        app.dependency_overrides.clear()

    def test_get_stock_history_success(self, mock_repo):
        """測試成功取得股價歷史"""
        # Mock Repository 回傳 DataFrame
        data = {
            "open": [100.0, 102.0],
            "high": [105.0, 108.0],
            "low": [99.0, 101.0],
            "close": [102.0, 106.0],
            "volume": [1000, 2000]
        }
        index = pd.DatetimeIndex(["2024-01-01", "2024-01-02"], name="date")
        df = pd.DataFrame(data, index=index)
        mock_repo.get_stock_data.return_value = df
        
        # Act
        response = client.get(
            "/api/v1/stocks/2330/history", 
            params={"start_date": "2024-01-01", "end_date": "2024-01-02"}
        )
        
        # Assert
        assert response.status_code == 200
        json_data = response.json()
        assert len(json_data) == 2
        # Pandas to_dict 會將 datetime 轉為 ISO 格式 (含時間)
        assert json_data[0]["date"].startswith("2024-01-01")
        assert json_data[0]["close"] == 102.0

    def test_get_stock_history_no_data(self, mock_repo):
        """測試無資料情況"""
        mock_repo.get_stock_data.return_value = pd.DataFrame()
        
        response = client.get(
            "/api/v1/stocks/2330/history",
            params={"start_date": "2024-01-01", "end_date": "2024-01-02"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "No data found"
