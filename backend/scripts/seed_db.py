#!/usr/bin/env python3
"""
資料庫 Seed Script

將模擬股價資料寫入 PostgreSQL 資料庫。
支援多檔股票：2330 (台積電), 2317 (鴻海), 2454 (聯發科)
"""
import os
import sys
from datetime import date, timedelta
import random

# 確保可以 import app 模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from app.core.database import SessionLocal, init_db
from app.modules.stock_data.repository import StockRepository
from app.models.stock import Stock


def generate_stock_data(ticker: str, start_date: date, end_date: date, base_price: float) -> pd.DataFrame:
    """
    生成模擬股價資料
    
    Args:
        ticker: 股票代碼
        start_date: 開始日期
        end_date: 結束日期
        base_price: 基準價格
    
    Returns:
        pd.DataFrame: 模擬股價資料
    """
    dates = []
    current = start_date
    while current <= end_date:
        # 跳過週末
        if current.weekday() < 5:
            dates.append(current)
        current += timedelta(days=1)
    
    # 生成隨機股價走勢
    price = base_price
    data = []
    
    for d in dates:
        # 每日漲跌幅 -3% ~ +3%
        change = random.uniform(-0.03, 0.03)
        price = price * (1 + change)
        
        # 計算 OHLC
        daily_volatility = random.uniform(0.005, 0.02)
        open_price = price * (1 + random.uniform(-daily_volatility, daily_volatility))
        high_price = max(open_price, price) * (1 + random.uniform(0, daily_volatility))
        low_price = min(open_price, price) * (1 - random.uniform(0, daily_volatility))
        close_price = price
        volume = random.randint(10000, 100000) * 1000
        
        data.append({
            'date': d,
            'open': float(round(open_price, 2)),
            'high': float(round(high_price, 2)),
            'low': float(round(low_price, 2)),
            'close': float(round(close_price, 2)),
            'volume': int(volume)
        })
    
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    return df


def seed_database():
    """執行資料庫 Seed"""
    print("🚀 開始資料庫初始化與 Seed...")
    
    # 初始化資料庫 (建立資料表)
    init_db()
    print("✅ 資料表建立完成")
    
    # 建立 Session
    db = SessionLocal()
    repo = StockRepository(db)
    
    # 定義要生成的股票
    stocks = [
        {"ticker": "2330", "name": "台積電", "market": "TWSE", "industry": "半導體", "base_price": 500.0},
        {"ticker": "2317", "name": "鴻海", "market": "TWSE", "industry": "電子零組件", "base_price": 100.0},
        {"ticker": "2454", "name": "聯發科", "market": "TWSE", "industry": "半導體", "base_price": 800.0},
    ]
    
    start_date = date(2023, 1, 1)
    end_date = date(2024, 12, 31)
    
    # Step 1: 建立 Stock 記錄 (先滿足 FK 約束)
    print("📝 建立股票基本資料...")
    for stock in stocks:
        stock_record = Stock(
            ticker=stock['ticker'],
            name=stock['name'],
            market=stock['market'],
            industry=stock['industry']
        )
        db.merge(stock_record)
    db.commit()
    print("✅ 股票基本資料建立完成")
    
    # Step 2: 建立股價資料
    for stock in stocks:
        print(f"📊 生成 {stock['ticker']} ({stock['name']}) 股價資料...")
        df = generate_stock_data(
            ticker=stock['ticker'],
            start_date=start_date,
            end_date=end_date,
            base_price=stock['base_price']
        )
        
        print(f"   💾 寫入資料庫 ({len(df)} 筆)...")
        repo.save_stock_data(stock['ticker'], df)
        print(f"   ✅ {stock['ticker']} 完成")
    
    db.close()
    print("\n🎉 資料庫 Seed 完成！")


if __name__ == "__main__":
    seed_database()
