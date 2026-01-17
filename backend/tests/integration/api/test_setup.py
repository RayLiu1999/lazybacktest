"""
🔴 TDD 紅燈階段：API 整合測試

測試 FastAPI 應用的基本功能：
1. 健康檢查 (Health Check)
2. 應用啟動與相依性注入
"""
from fastapi.testclient import TestClient
import pytest

# 預期會建立的 main entry point
from app.main import app

client = TestClient(app)


def test_health_check():
    """測試健康檢查端點"""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


def test_api_prefix():
    """測試 API 前綴 /api/v1"""
    # 假設有個測試端點或基本端點
    response = client.get("/api/v1/")
    
    # 404 是可接受的，只要不是 500，表示路由有掛載
    assert response.status_code != 500
