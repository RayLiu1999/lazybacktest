import { useState } from 'react';
import BacktestForm from './components/BacktestForm';
import EquityChart from './components/EquityChart';
import MetricsCard from './components/MetricsCard';
import type { BacktestRequest, BacktestResult } from './types/api';
import { runBacktest } from './services/api';
import './App.css';

function App() {
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (request: BacktestRequest) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await runBacktest(request);
      setResult(data);
    } catch (err) {
      console.error('Backtest error:', err);
      setError(err instanceof Error ? err.message : '回測執行失敗，請檢查後端服務是否運行中');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🚀 LazyBacktest</h1>
        <p>輕鬆回測你的投資策略</p>
      </header>

      <main className="app-main">
        <aside className="sidebar">
          <BacktestForm onSubmit={handleSubmit} isLoading={isLoading} />
        </aside>

        <section className="content">
          {isLoading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>正在執行回測...</p>
            </div>
          )}

          {error && (
            <div className="error-message">
              <span>⚠️</span>
              <p>{error}</p>
            </div>
          )}

          {result && !isLoading && (
            <>
              <MetricsCard result={result} />
              <EquityChart
                data={result.equity_curve}
                initialCapital={100000}
              />

              <div className="trades-section">
                <h3>📝 交易記錄</h3>
                <div className="trades-table-container">
                  <table className="trades-table">
                    <thead>
                      <tr>
                        <th>日期</th>
                        <th>類型</th>
                        <th>價格</th>
                        <th>數量</th>
                        <th>損益</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.trades.map((trade, index) => (
                        <tr key={index}>
                          <td>{trade.date}</td>
                          <td className={trade.type === 'BUY' ? 'buy' : 'sell'}>
                            {trade.type === 'BUY' ? '買入' : '賣出'}
                          </td>
                          <td>${trade.price.toFixed(2)}</td>
                          <td>{trade.quantity}</td>
                          <td className={trade.profit && trade.profit >= 0 ? 'profit' : 'loss'}>
                            {trade.profit ? `$${trade.profit.toFixed(0)}` : '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}

          {!result && !isLoading && !error && (
            <div className="placeholder">
              <div className="placeholder-icon">📊</div>
              <h2>開始你的第一次回測</h2>
              <p>在左側設定參數，點擊「開始回測」查看結果</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
