# LazyBacktest 系統規格文件

> 📅 最後更新: 2026-01-17
> 🏗️ 版本: v0.1.0 (Phase 9 Completed)

---

## 1. 專案概觀 (Project Overview)
**LazyBacktest** 是一個專為台股設計的輕量級、模組化回測系統。旨在提供直覺的 Web 介面，讓使用者能快速測試交易策略、視覺化績效指標，並進行參數優化 (Grid Search)。

### 主要特色
- **Web 介面**: 現代化 React UI，支援多頁籤 (摘要、績效、交易記錄、參數優化)。
- **SaaS 架構準備**: 資料庫設計預留多用戶 (Multi-tenant) 與策略儲存功能。
- **本地優先**: 極簡配置，支援 Docker 一鍵啟動。
- **資料彈性**: 支援 PostgreSQL 資料庫 (Production) 與 CSV 檔案 (Dev/Testing)。

---

## 2. 系統架構 (System Architecture)

### 技術堆疊 (Tech Stack)
| 層級 | 技術 | 說明 |
|------|------|------|
| **Frontend** | React 18, TypeScript, Vite | TailwindCSS 樣式, Recharts 圖表 |
| **Backend** | Python 3.13, FastAPI | Pydantic 資料驗證, SQLAlchemy ORM |
| **Database** | PostgreSQL | 交易資料, 用戶設定 (可選) |
| **Data Sci** | Pandas, NumPy | 高效能向量化回測運算 |
| **Testing** | Pytest, Vitest | 單元測試與整合測試 |

---

## 3. 功能規格 (Functional Specifications)

### 3.1 核心回測 (Backtesting Engine)
- **交易時機**: 支援 `N_CLOSE` (當日收盤價) 與 `N1_OPEN` (隔日開盤價)。
- **交易成本**: 支援客製化手續費 (買/賣) 與交易稅。
- **風險管理**:
  - `Position Sizing`: 依初始資金或總資金百分比進行部位控管。
  - `Stop Loss / Take Profit`: 固定百分比停損停利 (整合至 Engine 層)。
- **策略引擎**:
  - `StrategyRegistry`: 動態載入策略 (SMA, RSI, MACD, KD, Bollinger, Breakout)。
  - `Separate Entry/Exit`: 支援進出場策略分離 (例如: SMA 進場 + RSI 出場)。

### 3.2 績效指標 (Performance Metrics)
- **基礎指標**: 總報酬率, 年化報酬率 (CAGR), 最大回撤 (MDD), 勝率, 交易次數。
- **進階指標**: 
  - `Sharpe Ratio`: 承擔每單位風險的超額報酬。
  - `Sortino Ratio`: 僅考慮下檔風險的報酬比率。
  - `Buy & Hold Return`: 基準對照 (買入持有)。
- **視覺化**:
  - 淨值曲線圖 (Equity Curve)
  - 年度報酬柱狀圖 (Yearly Returns)
  - 月度報酬熱力圖表 (Monthly Returns)

### 3.3 參數優化 (Parameter Optimization)
- **Grid Search**: 網格搜索，測試所有參數組合。
- **Ranking**: 自動依 `Sharpe Ratio` 排序優化結果。
- **GUI**: 提供參數範圍輸入 (Min, Max, Step) 與即時運算。

---

## 4. 資料庫設計 (Database Schema)

雖然目前版本尚未開放公開註冊功能，但系統設計之初已導入完整的 SaaS 模型，以支援未來擴充。

### 4.1 股票資料 (Market Data)
- **`stocks`**: 股票基本資料 (代碼, 名稱, 市場, 產業)。
- **`stock_prices`**: 歷史股價 (OHLCV)，以 (Ticker, Date) 為複合主鍵。

### 4.2 用戶系統 (User System)
> ⚠️ **目前狀態**: 基礎建設已就緒，API 尚未實作登入/註冊端點。
- **`users`**: 用戶帳號系統 (Email, Password Hash)。
- **`strategies`**: 讓用戶儲存自定義策略參數與回測設定。

**Q: 為什麼有這兩張表？**
> 為了讓 LazyBacktest 具備 "雲端儲存" 能力。未來使用者可以：
> 1. 保存自己精心調教的策略參數。
> 2. 建立多組回測配置 (Config)。
> 3. 系統可升級為多用戶 SaaS 服務。

---

## 5. API 規格 (API Service)

### 5.1 回測服務
- `POST /api/v1/backtest/run`: 執行單次回測，回傳完整交易明細與指標。
- `POST /api/v1/backtest/optimize`: 執行 Grid Search，回傳參數組合列表。

### 5.2 資料服務
- `GET /api/v1/stocks/{ticker}/history`: 取得 K 線圖資料。
