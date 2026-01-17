# LazyBacktest 台股回測系統

透過歷史數據驗證您的交易策略，做出更明智的投資決策。

## 技術棧

- **後端**: Python 3.11+ / FastAPI
- **資料庫**: PostgreSQL + Redis
- **前端**: React + TypeScript

## 開發環境設定

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -e ".[dev]"
```

## 執行測試 (TDD)

```bash
pytest                      # 執行所有測試
pytest -v                   # 詳細輸出
pytest --cov=app            # 覆蓋率報告
pytest -k "test_sma"        # 執行特定測試
```

## 專案結構

```
lazybacktest/
├── backend/
│   ├── app/
│   │   ├── modules/
│   │   │   ├── backtest/      # 回測引擎
│   │   │   ├── stock_data/    # 股票資料
│   │   │   ├── strategy/      # 策略管理
│   │   │   └── user/          # 用戶管理
│   │   └── shared/            # 共用組件
│   └── tests/
│       ├── unit/              # 單元測試
│       └── integration/       # 整合測試
└── frontend/                  # React 前端
```
