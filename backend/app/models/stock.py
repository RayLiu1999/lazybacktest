"""
股票模型定義
"""
from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey, DECIMAL, BigInteger
from sqlalchemy.orm import relationship

from app.core.database import Base


class Stock(Base):
    """
    股票基本資料
    """
    __tablename__ = "stocks"

    ticker = Column(String(10), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    market = Column(String(10), nullable=False)  # 'TWSE', 'TPEx'
    industry = Column(String(50), nullable=True)

    # 關聯
    prices = relationship("StockPrice", back_populates="stock", cascade="all, delete-orphan")


class StockPrice(Base):
    """
    股價歷史資料
    """
    __tablename__ = "stock_prices"

    # 複合主鍵通常在 DB 層設，但在 ORM 我們可以用偽 ID 或複合主鍵定義
    # 這裡簡化，假設 (ticker, date) 是唯一
    ticker = Column(String(10), ForeignKey("stocks.ticker"), primary_key=True)
    date = Column(Date, primary_key=True)
    
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    adj_close = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=False)

    # 關聯
    stock = relationship("Stock", back_populates="prices")
