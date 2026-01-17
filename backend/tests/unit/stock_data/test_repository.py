"""
🔴 TDD 紅燈階段：Repository 資料存取層測試

測試 StockRepository 的功能：
1. 儲存股價資料 (DataFrame -> DB)
2. 讀取股價資料 (DB -> DataFrame)
3. 快取機制 (Mock Redis)
"""
import pytest
import pandas as pd
from datetime import date
from unittest.mock import Mock, patch
from sqlalchemy import select

from app.modules.stock_data.repository import StockRepository
from app.models.stock import Stock, StockPrice

class TestStockRepository:
    
    @pytest.fixture
    def mock_db_session(self):
        return Mock()
        
    @pytest.fixture
    def mock_redis(self):
        return Mock()
        
    @pytest.fixture
    def sample_df(self):
        data = {
            "open": [100.0, 102.0],
            "high": [105.0, 108.0],
            "low": [99.0, 101.0],
            "close": [102.0, 106.0],
            "volume": [1000, 2000]
        }
        index = pd.DatetimeIndex(["2024-01-01", "2024-01-02"], name="date")
        return pd.DataFrame(data, index=index)

    def test_save_stock_data(self, mock_db_session, mock_redis, sample_df):
        """測試儲存股價資料"""
        repo = StockRepository(mock_db_session, mock_redis)
        ticker = "2330"
        
        # 執行儲存
        repo.save_stock_data(ticker, sample_df)
        
        # 驗證 DB 操作
        # 實作使用 merge 方法來儲存（避免重複主鍵錯誤）
        assert mock_db_session.merge.called
        assert mock_db_session.commit.called
        
        # 驗證清除快取
        mock_redis.delete.assert_called_with(f"stock:{ticker}")

    def test_get_stock_data_cache_hit(self, mock_db_session, mock_redis, sample_df):
        """測試讀取資料 (快取命中)"""
        repo = StockRepository(mock_db_session, mock_redis)
        ticker = "2330"
        start = date(2024, 1, 1)
        end = date(2024, 1, 2)
        
        # Mock Redis 回傳
        mock_redis.get.return_value = sample_df.to_json()
        
        # 執行讀取
        df = repo.get_stock_data(ticker, start, end)
        
        # 驗證
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        # 不應該查詢 DB
        assert not mock_db_session.execute.called

    def test_get_stock_data_cache_miss(self, mock_db_session, mock_redis, sample_df):
        """測試讀取資料 (快取未命中 -> 查 DB)"""
        repo = StockRepository(mock_db_session, mock_redis)
        ticker = "2330"
        start = date(2024, 1, 1)
        end = date(2024, 1, 2)
        
        # Mock Redis Miss
        mock_redis.get.return_value = None
        
        # Mock DB Result
        # 模擬 SQLAlchemy result.scalars().all()
        # 這裡簡化 Mock 結構
        mock_result = Mock()
        mock_objects = [
            StockPrice(ticker="2330", date=date(2024, 1, 1), open=100, high=105, low=99, close=102, volume=1000),
            StockPrice(ticker="2330", date=date(2024, 1, 2), open=102, high=108, low=101, close=106, volume=2000)
        ]
        mock_result.scalars.return_value.all.return_value = mock_objects
        mock_db_session.execute.return_value = mock_result
        
        # 執行讀取
        df = repo.get_stock_data(ticker, start, end)
        
        # 驗證
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert mock_db_session.execute.called
        # 應該設定快取
        assert mock_redis.set.called
