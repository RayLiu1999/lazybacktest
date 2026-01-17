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
      setError(err instanceof Error ? err.message : '回測執行失敗');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-teal-500 rounded-lg flex items-center justify-center text-white font-bold text-sm">
              📈
            </div>
            <span className="text-xl font-bold text-gray-800">LazyBacktest</span>
          </div>
          <div className="text-sm text-gray-500">股票回測工具</div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-b from-gray-50 to-gray-100 py-12 text-center border-b border-gray-200">
        <h1 className="text-3xl font-bold text-gray-800 mb-3">股票回測工具</h1>
        <p className="text-gray-500 mb-6">透過歷史數據驗證您的交易策略，做出更明智的投資決策</p>
        <button
          onClick={() => handleSubmit({
            ticker: '2330',
            start_date: '2024-01-01',
            end_date: '2024-12-31',
            initial_capital: 100000,
            strategy: { name: 'sma_crossover', params: { short_period: 5, long_period: 20 } }
          })}
          className="bg-teal-500 hover:bg-teal-600 text-white font-semibold px-6 py-3 rounded-lg shadow-sm transition-colors"
        >
          🚀 一鍵回測台積電
        </button>
      </section>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Left Panel - Settings */}
          <aside className="w-full lg:w-80 lg:flex-shrink-0">
            <div className="lg:sticky lg:top-6 space-y-6">
              <BacktestForm onSubmit={handleSubmit} isLoading={isLoading} />
            </div>
          </aside>

          {/* Right Panel - Results */}
          <section className="flex-1 min-w-0">
            {/* Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
                <strong>錯誤：</strong> {error}
              </div>
            )}

            {/* Loading */}
            {isLoading && (
              <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
                <div className="inline-block w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                <p className="text-gray-500">回測執行中...</p>
              </div>
            )}

            {/* Results */}
            {result && !isLoading && (
              <div className="space-y-6">
                {/* Tabs */}
                <div className="flex gap-1 border-b border-gray-200">
                  <button className="px-4 py-2 text-sm font-medium text-teal-600 border-b-2 border-teal-500">
                    📊 績效分析
                  </button>
                  <button className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700">
                    📝 交易記錄
                  </button>
                </div>

                {/* Metrics */}
                <MetricsCard result={result} />

                {/* Chart */}
                <div className="bg-white rounded-xl border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">淨值曲線圖</h3>
                  <EquityChart data={result.equity_curve} initialCapital={100000} />
                </div>

                {/* Trade Log */}
                <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                  <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                    <h3 className="text-lg font-semibold text-gray-800">交易記錄</h3>
                  </div>
                  <div className="divide-y divide-gray-100">
                    {result.trades.map((trade, index) => (
                      <div key={index} className="px-6 py-4 flex items-center justify-between hover:bg-gray-50">
                        <div className="flex items-center gap-4">
                          <span className={`px-2 py-1 text-xs font-medium rounded ${trade.type === 'BUY'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-red-100 text-red-700'
                            }`}>
                            {trade.type === 'BUY' ? '買入' : '賣出'}
                          </span>
                          <span className="text-gray-600">{trade.date}</span>
                        </div>
                        <div className="flex items-center gap-6 text-sm">
                          <span className="text-gray-500">${trade.price.toFixed(2)}</span>
                          <span className="text-gray-500">{trade.quantity} 股</span>
                          {trade.profit !== null && trade.profit !== undefined && (
                            <span className={trade.profit >= 0 ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
                              {trade.profit > 0 ? '+' : ''}{trade.profit.toFixed(0)}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Empty State */}
            {!result && !isLoading && !error && (
              <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="text-3xl">📊</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">執行回測後將顯示淨值曲線</h3>
                <p className="text-gray-500">在左側設定參數後點擊「開始回測」</p>
              </div>
            )}
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white mt-12">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-gray-500">
            <span>© 2026 LazyBacktest - 台股回測系統</span>
            <span>v0.1.0</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
