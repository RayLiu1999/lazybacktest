"""
股價資料存取層 (Repository Pattern)

負責資料庫操作與快取策略。
"""
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from datetime import date
import pandas as pd
import json
from typing import Optional, Any
from app.models.stock import StockPrice

class StockRepository:
    """
    股價資料 Repository
    
    Attributes:
        db: SQLAlchemy Session
        redis: Redis client (optional)
    """
    
    def __init__(self, db: Session, redis: Any = None):
        self.db = db
        self.redis = redis
        self.CACHE_EXPIRE = 3600  # 快取 1 小時

    def save_stock_data(self, ticker: str, df: pd.DataFrame) -> None:
        """
        儲存股價資料到資料庫
        
        Args:
            ticker: 股票代碼
            df: 包含股價資料的 DataFrame (index 為 date)
        """
        stock_prices = []
        for index, row in df.iterrows():
            ensure_date = index.date() if isinstance(index, pd.Timestamp) else index
            
            # 建立 StockPrice 物件 (確保轉換 numpy 類型為 Python 原生類型)
            price = StockPrice(
                ticker=ticker,
                date=ensure_date,
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                adj_close=float(row['adj_close']) if 'adj_close' in row and pd.notna(row['adj_close']) else None,
                volume=int(row['volume']),
                dividends=float(row['dividends']) if 'dividends' in row and pd.notna(row['dividends']) else 0.0,
                stock_splits=float(row['stock_splits']) if 'stock_splits' in row and pd.notna(row['stock_splits']) else 0.0
            )
            stock_prices.append(price)
            
        # 批量儲存
        # 為了效能，先生產環境可以用 bulk_insert_mappings，這裡用 merge 或 add_all
        # 簡單起見先用 merge 避免重複主鍵錯誤（雖然較慢）
        for price in stock_prices:
             self.db.merge(price)
             
        self.db.commit()
        
        # 清除快取
        if self.redis:
            self.redis.delete(f"stock:{ticker}")

    def get_stock_data(self, ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
        """
        取得股價資料 (優先讀取快取)
        
        Args:
            ticker: 股票代碼
            start_date: 開始日期
            end_date: 結束日期
            
        Returns:
            pd.DataFrame: 股價資料
        """
        cache_key = f"stock:{ticker}:{start_date}:{end_date}"
        
        # 1. 嘗試讀取快取
        if self.redis:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                # 從 JSON 載入，並重建日期索引
                df = pd.read_json(cached_data)
                if not df.empty:
                    # 確保 index 是 datetime 且名稱正確
                    if df.index.name != 'date':
                        # 有時 read_json 會把 index 放進 column
                        pass 
                    return df

        # 2. 讀取資料庫
        stmt = select(StockPrice).where(
            and_(
                StockPrice.ticker == ticker,
                StockPrice.date >= start_date,
                StockPrice.date <= end_date
            )
        ).order_by(StockPrice.date)
        
        result = self.db.execute(stmt)
        prices = result.scalars().all()
        
        if not prices:
            # Fallback 1: 嘗試使用 yfinance 即時抓取
            from app.modules.stock_data.fetcher import StockDataFetcher
            fetcher = StockDataFetcher()
            df = fetcher.fetch(ticker, str(start_date), str(end_date))
            
            if not df.empty:
                # Auto-cache: 儲存到資料庫供下次使用
                try:
                    self.save_stock_data(ticker, df)
                except Exception as e:
                    # 快取失敗不影響回傳結果
                    print(f"Cache save failed for {ticker}: {e}")
                return df
            
            # Fallback 2: 嘗試讀取 CSV 檔案 (for development/demo)
            import os
            csv_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                "scripts",
                f"seed_data_{ticker}.csv"
            )
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
                # 過濾日期範圍
                df = df[(df.index >= pd.Timestamp(start_date)) & (df.index <= pd.Timestamp(end_date))]
                return df
            return pd.DataFrame()
            
        # 轉換為 DataFrame
        data = [
            {
                "date": p.date,
                "open": p.open,
                "high": p.high,
                "low": p.low,
                "close": p.close,
                "adj_close": p.adj_close,
                "volume": p.volume,
                "dividends": float(p.dividends) if p.dividends else 0.0,
                "stock_splits": float(p.stock_splits) if p.stock_splits else 0.0
            }
            for p in prices
        ]
        
        df = pd.DataFrame(data)
        df.set_index("date", inplace=True)
        
        # 3. 寫入快取
        if self.redis:
            self.redis.set(cache_key, df.to_json(), ex=self.CACHE_EXPIRE)
            
        return df
