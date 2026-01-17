"""
策略模型定義
"""
from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class Strategy(Base):
    """
    用戶策略資料表
    """
    __tablename__ = "strategies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    config = Column(JSON, nullable=False)  # 儲存策略完整配置 (JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    user = relationship("User", back_populates="strategies")
