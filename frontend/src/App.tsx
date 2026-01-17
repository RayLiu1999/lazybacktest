import { useState } from 'react';
import BacktestForm from './components/BacktestForm';
import EquityChart from './components/EquityChart';
import MetricsCard from './components/MetricsCard';
import type { BacktestRequest, BacktestResult } from './types/api';
import { runBacktest } from './services/api';

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
    <div className="min-h-screen flex flex-col bg-slate-950">
      {/* Header */}
      <header className="px-8 py-6 bg-gradient-to-r from-slate-900 to-slate-800 border-b border-slate-700/50">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
          🚀 LazyBacktest
        </h1>
        <p className="text-slate-400 text-sm mt-1">輕鬆回測你的投資策略</p>
      </header>

      {/* Main Content */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-[400px_1fr] gap-8 p-8">
        {/* Sidebar - Form */}
        <aside className="lg:sticky lg:top-8 h-fit">
          <BacktestForm onSubmit={handleSubmit} isLoading={isLoading} />
        </aside>

        {/* Content Area */}
        <section className="min-h-[400px]">
          {/* Loading State */}
          {isLoading && (
            <div className="flex flex-col items-center justify-center h-80 text-slate-400">
              <div className="w-12 h-12 border-3 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin mb-4" />
              <p>正在執行回測...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="flex items-center gap-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
              <span className="text-2xl">⚠️</span>
              <p>{error}</p>
            </div>
          )}

          {/* Results */}
          {result && !isLoading && (
            <div className="space-y-6">
              <MetricsCard result={result} />
              <EquityChart data={result.equity_curve} initialCapital={100000} />

              {/* Trades Table */}
              <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl p-6">
                <h3 className="text-cyan-400 text-lg font-semibold mb-4">📝 交易記錄</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="text-slate-400 text-sm uppercase border-b border-slate-700/50">
                        <th className="py-3 px-4 text-left">日期</th>
                        <th className="py-3 px-4 text-left">類型</th>
                        <th className="py-3 px-4 text-left">價格</th>
                        <th className="py-3 px-4 text-left">數量</th>
                        <th className="py-3 px-4 text-left">損益</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.trades.map((trade, index) => (
                        <tr key={index} className="border-b border-slate-700/30">
                          <td className="py-3 px-4 text-slate-300">{trade.date}</td>
                          <td className={`py-3 px-4 ${trade.type === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                            {trade.type === 'BUY' ? '買入' : '賣出'}
                          </td>
                          <td className="py-3 px-4 text-slate-300">${trade.price.toFixed(2)}</td>
                          <td className="py-3 px-4 text-slate-300">{trade.quantity}</td>
                          <td className={`py-3 px-4 ${trade.profit && trade.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {trade.profit ? `$${trade.profit.toFixed(0)}` : '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Placeholder */}
          {!result && !isLoading && !error && (
            <div className="flex flex-col items-center justify-center h-96 text-slate-500">
              <div className="text-6xl mb-4 opacity-50">📊</div>
              <h2 className="text-xl text-white mb-2">開始你的第一次回測</h2>
              <p>在左側設定參數，點擊「開始回測」查看結果</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
