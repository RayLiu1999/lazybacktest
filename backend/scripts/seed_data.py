"""
資料填充腳本：使用 FinMind API 抓取台股 2330 股價資料
"""
import requests
import pandas as pd
from datetime import datetime
import sys
import os

# 加入專案路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modules.stock_data.fetcher import StockDataFetcher

def seed_stock_data():
    """填充 2330 台積電股價資料"""
    print("🚀 開始抓取股價資料...")
    
    fetcher = StockDataFetcher()
    
    # 抓取 2024 年資料
    try:
        df = fetcher.fetch("2330", "2024-01-01", "2024-12-31")
        
        if df.empty:
            print("❌ 無法取得資料，嘗試使用模擬資料...")
            # 使用模擬資料
            df = generate_mock_data()
        
        print(f"✅ 成功抓取 {len(df)} 筆資料")
        print(df.head())
        
        # 儲存為 CSV 供後續使用
        output_path = os.path.join(os.path.dirname(__file__), "seed_data_2330.csv")
        df.to_csv(output_path, index=True)
        print(f"💾 資料已儲存至: {output_path}")
        
        return df
        
    except Exception as e:
        print(f"❌ 抓取失敗: {e}")
        print("📊 使用模擬資料...")
        df = generate_mock_data()
        
        output_path = os.path.join(os.path.dirname(__file__), "seed_data_2330.csv")
        df.to_csv(output_path, index=True)
        print(f"💾 模擬資料已儲存至: {output_path}")
        
        return df


def generate_mock_data():
    """生成模擬股價資料"""
    import numpy as np
    
    # 生成 2024 年的交易日 (約 250 天)
    dates = pd.date_range(start="2024-01-02", end="2024-12-31", freq="B")[:248]
    
    # 模擬股價走勢 (以 600 為基準，有上漲趨勢)
    np.random.seed(42)
    base_price = 600
    returns = np.random.normal(0.0005, 0.015, len(dates))  # 日報酬率
    cumulative = np.cumprod(1 + returns)
    close_prices = base_price * cumulative
    
    # 計算 OHLC
    df = pd.DataFrame({
        "date": dates,
        "open": close_prices * (1 + np.random.uniform(-0.005, 0.005, len(dates))),
        "high": close_prices * (1 + np.random.uniform(0.002, 0.02, len(dates))),
        "low": close_prices * (1 - np.random.uniform(0.002, 0.02, len(dates))),
        "close": close_prices,
        "volume": np.random.randint(10000, 50000, len(dates)) * 1000,
    })
    
    df = df.set_index("date")
    df.index.name = "date"
    
    return df


if __name__ == "__main__":
    seed_stock_data()
