"""
股價資料抓取模組

負責從外部 API 抓取股價歷史資料並正規化。
目前支援來源：FinMind
"""
import httpx
import pandas as pd
from datetime import date
from dataclasses import dataclass


@dataclass
class StockData:
    """股價資料結構"""
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockDataFetcher:
    """
    股價抓取服務
    """
    
    BASE_URL = "https://api.finmindtrade.com/api/v4/data"
    
    async def fetch_data(self, ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
        """
        抓取指定期間的股價資料
        
        Args:
            ticker: 股票代碼 (Ex: 2330)
            start_date: 開始日期
            end_date: 結束日期
            
        Returns:
            pd.DataFrame: 包含 open, high, low, close, volume 的 DataFrame，index 為 date
            
        Raises:
            ValueError: 查無資料
            ConnectionError: API 連線失敗
        """
        params = {
            "dataset": "TaiwanStockPrice",
            "data_id": ticker,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.BASE_URL, params=params)
                
                if response.status_code != 200:
                    raise ConnectionError(f"API Error: {response.status_code}")
                
                data = response.json()
                
        except httpx.RequestError as e:
            raise ConnectionError(f"Network error: {str(e)}")
            
        if "data" not in data or not data["data"]:
            raise ValueError(f"No data found for {ticker}")
            
        df = pd.DataFrame(data["data"])
        
        # 資料清洗與重命名
        # FinMind 欄位: date, stock_id, Trading_Volume, Trading_money, open, max, min, close, spread, Trading_turnover
        
        df = df.rename(columns={
            "max": "high",
            "min": "low",
            "Trading_Volume": "volume"
        })
        
        # 轉換日期索引
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        
        # 確保數值型別
        numeric_cols = ["open", "high", "low", "close", "volume"]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        
        # 選取需要的欄位
        return df[["open", "high", "low", "close", "volume"]]
