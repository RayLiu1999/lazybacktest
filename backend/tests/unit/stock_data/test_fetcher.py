"""
🔴 TDD 紅燈階段：股價資料抓取服務測試

測試從外部來源抓取資料並轉換為標準格式的邏輯。
使用 Mock 來模擬外部 API 回應，不依賴真實網路。
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, AsyncMock
from datetime import date

from app.modules.stock_data.fetcher import StockDataFetcher, StockData


class TestStockDataFetcher:
    """股價抓取服務測試"""
    
    @pytest.fixture
    def mock_response_data(self):
        """模擬 API 回應資料 (FinMind 格式範例)"""
        return {
            "msg": "success",
            "status": 200,
            "data": [
                {
                    "date": "2024-01-01",
                    "stock_id": "2330",
                    "Trading_Volume": 1000,
                    "Trading_money": 100000,
                    "open": 100.0,
                    "max": 105.0,
                    "min": 99.0,
                    "close": 102.0,
                    "spread": 2.0,
                    "Trading_turnover": 10
                },
                {
                    "date": "2024-01-02",
                    "stock_id": "2330",
                    "Trading_Volume": 2000,
                    "Trading_money": 200000,
                    "open": 102.0,
                    "max": 108.0,
                    "min": 101.0,
                    "close": 106.0,
                    "spread": 4.0,
                    "Trading_turnover": 20
                }
            ]
        }

    @pytest.mark.asyncio
    @patch("app.modules.stock_data.fetcher.httpx.AsyncClient")
    async def test_fetch_stock_data_success(self, mock_client_class, mock_response_data):
        """測試成功抓取並轉換資料"""
        # Arrange: 正確設定 AsyncMock
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.status_code = 200
        
        # 使用 AsyncMock 讓 get() 返回 awaitable
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        
        # __aenter__ 返回 mock_client
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        fetcher = StockDataFetcher()
        
        # Act: 執行抓取
        df = await fetcher.fetch_data("2330", date(2024, 1, 1), date(2024, 1, 2))
        
        # Assert: 驗證結果
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "open" in df.columns
        assert "close" in df.columns
        assert df.iloc[0]["close"] == 102.0
        assert df.iloc[1]["close"] == 106.0
        
        # 驗證日期索引
        assert df.index.name == "date"
        assert pd.Timestamp("2024-01-01") in df.index

    @pytest.mark.asyncio
    @patch("app.modules.stock_data.fetcher.httpx.AsyncClient")
    async def test_fetch_stock_data_empty(self, mock_client_class):
        """測試抓取無資料情況"""
        mock_response = Mock()
        mock_response.json.return_value = {"msg": "success", "data": []}
        mock_response.status_code = 200
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        fetcher = StockDataFetcher()
        
        with pytest.raises(ValueError, match="No data found"):
            await fetcher.fetch_data("2330", date(2024, 1, 1), date(2024, 1, 1))

    @pytest.mark.asyncio
    @patch("app.modules.stock_data.fetcher.httpx.AsyncClient")
    async def test_fetch_stock_data_api_error(self, mock_client_class):
        """測試 API 錯誤情況"""
        mock_response = Mock()
        mock_response.status_code = 500
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        fetcher = StockDataFetcher()
        
        with pytest.raises(ConnectionError):
            await fetcher.fetch_data("2330", date(2024, 1, 1), date(2024, 1, 1))
