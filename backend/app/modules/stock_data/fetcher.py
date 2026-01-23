"""
股價資料抓取模組

使用 yfinance 抓取台股與全球股價資料。
台股代碼需加上 .TW 後綴 (例: 2330.TW)
"""
import yfinance as yf
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
    股價抓取服務 (yfinance 版本)
    
    支援台股 (需加 .TW) 與全球股票。
    """
    
    def fetch(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        同步抓取指定期間的股價資料
        
        Args:
            ticker: 股票代碼 (Ex: 2330 或 2330.TW 或 AAPL)
            start_date: 開始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)
            
        Returns:
            pd.DataFrame: 包含 open, high, low, close, volume 的 DataFrame，index 為 date
        """
        # 自動補上台股後綴
        yf_ticker = self._normalize_ticker(ticker)
        
        try:
            stock = yf.Ticker(yf_ticker)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                return pd.DataFrame()
            
            # yfinance 欄位: Open, High, Low, Close, Volume, Dividends, Stock Splits
            # 重新命名並保留完整資料 (包含 Adj Close, Dividends, Stock Splits)
            df = df.rename(columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
                "Dividends": "dividends",
                "Stock Splits": "stock_splits"
            })
            
            # 計算 adj_close (yfinance 不直接提供,需透過 Close 與除權息調整)
            # 若 yfinance 有提供 Adj Close,則直接使用
            if "Adj Close" in stock.history(start=start_date, end=end_date).columns:
                df["adj_close"] = stock.history(start=start_date, end=end_date)["Adj Close"].values
            else:
                # Fallback: 使用 close 作為 adj_close
                df["adj_close"] = df["close"]
            
            # 選取需要的欄位 (保留完整資料)
            df = df[["open", "high", "low", "close", "adj_close", "volume", "dividends", "stock_splits"]]
            
            # 確保 index 名稱統一
            df.index.name = "date"
            
            return df
            
        except Exception as e:
            print(f"yfinance fetch error for {yf_ticker}: {e}")
            return pd.DataFrame()
    
    async def fetch_data(self, ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
        """
        非同步版本 (向後兼容)
        
        注意: yfinance 本身是同步的，這裡直接呼叫同步方法。
        """
        return self.fetch(
            ticker,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
    
    def _normalize_ticker(self, ticker: str) -> str:
        """
        正規化股票代碼
        
        台股代碼 (純數字) 自動加上 .TW 後綴
        """
        ticker = ticker.strip().upper()
        
        # 如果已經有後綴，直接返回
        if "." in ticker:
            return ticker
        
        # 純數字視為台股，加上 .TW
        if ticker.isdigit():
            return f"{ticker}.TW"
        
        # 其他情況視為國際股票，直接返回
        return ticker
