"""
用戶模型定義
"""
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class User(Base):
    """
    用戶資料表
    """
    __tablename__ = "users"

    # 使用 String 作為 ID 以兼容 SQLite (測試用) 與 PostgreSQL
    # 在 PG 中可以使用 UUID type
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 關聯
    strategies = relationship("Strategy", back_populates="user", cascade="all, delete-orphan")
