"""
🔴 TDD 紅燈階段：資料庫模型測試

測試 SQLAlchemy ORM 模型的定義與關聯：
1. User 模型：基本欄位與密碼雜湊
2. Stock 模型：股票基本資料
3. StockPrice 模型：股價歷史資料（與 Stock 關聯）
4. Strategy 模型：用戶策略（與 User 關聯）
"""
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from datetime import date, datetime

# 預期會建立的模組（目前尚未建立，會紅燈）
from app.models.user import User
from app.models.stock import Stock, StockPrice
from app.models.strategy import Strategy
from app.core.database import Base


# 測試用資料庫連接
@pytest.fixture(scope="function")
def db_session():
    """建立測試用記憶體 SQLite 資料庫"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


class TestUserModel:
    """用戶模型測試"""
    
    def test_create_user(self, db_session):
        """測試建立用戶"""
        user = User(
            email="test@example.com",
            password_hash="hashed_secret"
        )
        db_session.add(user)
        db_session.commit()
        
        saved_user = db_session.scalar(select(User).where(User.email == "test@example.com"))
        assert saved_user is not None
        assert saved_user.id is not None
        assert saved_user.email == "test@example.com"
        assert saved_user.created_at is not None

    def test_user_email_unique(self, db_session):
        """測試 Email 唯一性"""
        user1 = User(email="test@example.com", password_hash="pw1")
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(email="test@example.com", password_hash="pw2")
        db_session.add(user2)
        
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


class TestStockModel:
    """股票模型測試"""
    
    def test_create_stock_with_prices(self, db_session):
        """測試建立股票與股價關聯"""
        # 建立股票
        stock = Stock(
            ticker="2330",
            name="台積電",
            market="TWSE"
        )
        db_session.add(stock)
        db_session.commit()
        
        # 建立股價
        price1 = StockPrice(
            ticker="2330",
            date=date(2024, 1, 1),
            open=100, high=105, low=99, close=102,
            volume=1000
        )
        price2 = StockPrice(
            ticker="2330",
            date=date(2024, 1, 2),
            open=102, high=108, low=101, close=106,
            volume=2000
        )
        db_session.add_all([price1, price2])
        db_session.commit()
        
        # 驗證關聯
        saved_stock = db_session.scalar(select(Stock).where(Stock.ticker == "2330"))
        assert len(saved_stock.prices) == 2
        assert saved_stock.prices[0].close in [102, 106]


class TestStrategyModel:
    """策略模型測試"""
    
    def test_create_strategy(self, db_session):
        """測試建立策略與用戶關聯"""
        # 先建立用戶
        user = User(email="trader@example.com", password_hash="pw")
        db_session.add(user)
        db_session.commit()
        
        # 建立策略
        config = {"buy_signal": "golden_cross", "period": 20}
        strategy = Strategy(
            user_id=user.id,
            name="My Macbeth Strategy",
            config=config
        )
        db_session.add(strategy)
        db_session.commit()
        
        # 驗證
        saved_strategy = db_session.scalar(select(Strategy).where(Strategy.name == "My Macbeth Strategy"))
        assert saved_strategy.user_id == user.id
        assert saved_strategy.config["buy_signal"] == "golden_cross"
        
        # 驗證反向關聯
        assert len(user.strategies) == 1
        assert user.strategies[0].name == "My Macbeth Strategy"
