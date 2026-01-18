# 📈 LazyBacktest - 輕量級台股回測系統

這是一個專為台股設計的現代化回測系統，旨在提供直覺的 Web 介面，讓使用者能快速測試交易策略、視覺化績效指標，並進行參數優化。

## 🧠 設計模式與邏輯 (Core Design Patterns)

### 1. 單一部位原則 (One Position at a Time)
系統採用保守的資金管理邏輯，**同一時間僅持有一筆部位**。
- **邏輯**：當持倉 > 0 時，系統會忽略所有新的「買進」訊號，直到出現「賣出」訊號或觸發停損停利。
- **目的**：避免無限加碼導致風險失控，簡化回測變因。

### 2. 進出場分離 (Separate Entry/Exit)
策略的進場與出場邏輯是完全解耦的。
- **範例**：你可以設定「SMA 黃金交叉進場」，但使用「RSI 超買出場」或「固定 5% 停利」。
- **預設**：若未指定出場策略，系統預設使用進場策略的「反向訊號」作為出場 (例如 SMA 金叉買，死叉賣)。

### 3. 交易時機 (Timing)
支援兩種現實交易場景：
- **`N_CLOSE` (收盤價成交)**：訊號當日收盤價成交 (適合日 K 結束前操作)。
- **`N1_OPEN` (隔日開盤成交)**：訊號當日確認後，隔日開盤價成交 (實務上最常用)。

### 4. 資金管理 (Position Sizing)
- **`INITIAL_CAPITAL` (初始資金)**：每次交易以初始本金的 % 計算 (固定金額)。
- **`TOTAL_CAPITAL` (複利模式)**：每次交易以當前總資產的 % 計算 (隨淨值增減)。

---

## 🚀 主要功能 (Features)

- **多策略支援**: SMA, RSI, MACD, KD, Bollinger Bands, Price Breakout
- **參數優化**: 內建 Grid Search (網格搜索)，自動尋找最佳參數組合 (Sharpe Ratio 排序)
- **視覺化分析**: 
  - 淨值曲線 (Equity Curve)
  - 年度/月度報酬熱力圖
  - 9 大績效指標 (CAGR, MDD, Sharpe, Sortino...)
- **數據來源**: 
  - 優先讀取本地資料庫 (快取)
  - 自動串接 `yfinance` 抓取台股 (2330.TW) 與美股歷史資料
  - 支援 CSV 匯入作為 Fallback

---

## 🛠️ 技術棧 (Tech Stack)

- **Backend**: Python 3.13, FastAPI, SQLAlchemy, Pandas, NumPy
- **Frontend**: React 18, TypeScript, Vite, Recharts, TailwindCSS
- **Database**: PostgreSQL (Production) / SQLite (Test)

## 📦 快速開始 (Quick Start)

### 使用 Docker (推薦)

```bash
docker-compose up --build
```
啟動後訪問：`http://localhost:3000`

### 本地開發

**Backend**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## 🧪 測試 (TDD)

專案採用測試驅動開發 (TDD) 模式，擁有高覆蓋率的測試集。

```bash
# 後端測試
cd backend
pytest -v

# 前端測試
cd frontend
npm test
```
