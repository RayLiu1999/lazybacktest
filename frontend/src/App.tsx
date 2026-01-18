import { useState } from 'react';
import BacktestForm from './components/BacktestForm';
import SummaryTab from './components/tabs/SummaryTab';
import TradeLogsTab from './components/tabs/TradeLogsTab';
import OptimizationTab from './components/tabs/OptimizationTab';
import PerformanceTab from './components/tabs/PerformanceTab';
import type { BacktestRequest, BacktestResult } from './types/api';
import { runBacktest } from './services/api';

type Tab = 'SUMMARY' | 'PERFORMANCE' | 'LOGS' | 'OPTIMIZATION' | 'BATCH';

function App() {
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>('SUMMARY');
  const [lastRequest, setLastRequest] = useState<BacktestRequest | null>(null);

  const handleSubmit = async (request: BacktestRequest) => {
    setIsLoading(true);
    setError(null);
    setResult(null);
    setLastRequest(request);

    try {
      const data = await runBacktest(request);

      // Data transformer for API compatibility (if needed for old backend)
      // Ensure equity_curve is array of objects
      if (data.equity_curve && typeof data.equity_curve[0] === 'number') {
        const initialEquity = data.equity_curve[0] as unknown as number;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        data.equity_curve = (data.equity_curve as any as number[]).map((val: number, idx: number) => ({
          date: `Day ${idx + 1}`,
          equity: val,
          return_pct: ((val / initialEquity) - 1) * 100,
          drawdown: 0 // Mock drawdown if missing
        }));
      }

      setResult(data);
      setActiveTab('SUMMARY'); // Auto switch to summary on success
    } catch (err) {
      console.error('Backtest error:', err);
      setError(err instanceof Error ? err.message : '回測執行失敗');
    } finally {
      setIsLoading(false);
    }
  };

  const renderTabContent = () => {
    if (!result || !lastRequest) return null;

    switch (activeTab) {
      case 'SUMMARY':
        return <SummaryTab result={result} initialCapital={lastRequest.initial_capital} />;
      case 'PERFORMANCE':
        return <PerformanceTab result={result} />;
      case 'LOGS':
        return <TradeLogsTab result={result} />;
      case 'OPTIMIZATION':
        return (
          <OptimizationTab
            ticker={lastRequest.ticker}
            startDate={lastRequest.start_date}
            endDate={lastRequest.end_date}
            initialCapital={lastRequest.initial_capital}
          />
        );
      case 'BATCH':
        return <div className="text-gray-500 text-center py-10">批量優化功能開發中...</div>;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 font-sans">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 z-50 flex items-center px-6 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-teal-600 rounded-lg flex items-center justify-center text-white font-bold text-sm shadow-md">
            LB
          </div>
          <span className="text-xl font-bold text-gray-800 tracking-tight">LazyBacktest</span>
          <span className="text-xs px-2 py-0.5 bg-teal-50 text-teal-600 rounded-full border border-teal-100 font-medium">Phase 7 UI</span>
        </div>
        <div className="ml-auto text-sm text-gray-500 flex gap-4">
          <a href="#" className="hover:text-teal-600 transition-colors">使用教學</a>
          <a href="#" className="hover:text-teal-600 transition-colors">問題回報</a>
        </div>
      </header>

      <div className="pt-16 flex h-screen overflow-hidden">
        {/* Left Sidebar - Settings */}
        <aside className="w-[400px] flex-shrink-0 bg-white border-r border-gray-200 overflow-y-auto custom-scrollbar">
          <div className="p-6">
            <div className="mb-6">
              <h2 className="text-lg font-bold text-gray-800 mb-1">策略參數設定</h2>
              <p className="text-sm text-gray-500">設定回測條件與策略參數</p>
            </div>
            <BacktestForm onSubmit={handleSubmit} isLoading={isLoading} />
          </div>
        </aside>

        {/* Right Content - Results */}
        <main className="flex-1 overflow-y-auto bg-gray-50/50 p-8 custom-scrollbar relative">

          {/* Hero / Empty State */}
          {!result && !isLoading && !error && (
            <div className="max-w-3xl mx-auto text-center mt-20">
              <h1 className="text-4xl font-bold text-gray-800 mb-4">股票交易策略回測工具</h1>
              <p className="text-lg text-gray-500 mb-8 leading-relaxed">
                透過歷史數據驗證您的交易策略，提供完整的績效報告與視覺化分析。<br />
                支援多種技術指標策略與風險管理設定。
              </p>
              <div className="inline-flex gap-4">
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-100 w-40">
                  <div className="text-2xl mb-2">⚡️</div>
                  <div className="font-semibold text-gray-700">快速回測</div>
                </div>
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-100 w-40">
                  <div className="text-2xl mb-2">📊</div>
                  <div className="font-semibold text-gray-700">視覺化報表</div>
                </div>
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-100 w-40">
                  <div className="text-2xl mb-2">🛡️</div>
                  <div className="font-semibold text-gray-700">風險管理</div>
                </div>
              </div>
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="absolute inset-0 bg-white/50 backdrop-blur-sm flex items-center justify-center z-10 transition-all">
              <div className="flex flex-col items-center p-8 bg-white rounded-2xl shadow-2xl border border-gray-100">
                <div className="w-12 h-12 border-4 border-teal-500 border-t-transparent rounded-full animate-spin mb-4" />
                <h3 className="text-lg font-semibold text-gray-800">正在執行回測...</h3>
                <p className="text-gray-500 text-sm">正在計算策略績效與交易紀錄</p>
              </div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="max-w-4xl mx-auto mb-6 bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-xl flex items-center gap-3 shadow-sm">
              <span className="text-xl">⚠️</span>
              <div>
                <strong className="block font-semibold">回測執行發生錯誤</strong>
                <span className="text-sm opacity-90">{error}</span>
              </div>
            </div>
          )}

          {/* Results View */}
          {result && (
            <div className="max-w-6xl mx-auto space-y-6 pb-20">
              {/* Quick Summary Header */}
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-3">
                    {result.ticker} 回測報告
                    <span className={`text-sm px-2 py-0.5 rounded-full border ${result.total_return >= 0
                      ? 'bg-green-50 text-green-700 border-green-200'
                      : 'bg-red-50 text-red-700 border-red-200'
                      }`}>
                      {result.total_return >= 0 ? '獲利' : '虧損'}
                    </span>
                  </h2>
                  <p className="text-sm text-gray-500 mt-1">
                    初始資金: ${lastRequest?.initial_capital.toLocaleString()} |
                    期間: {lastRequest?.start_date} ~ {lastRequest?.end_date}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 transition-colors">
                    匯出報告
                  </button>
                </div>
              </div>

              {/* Tabs Navigation */}
              <div className="flex gap-1 border-b border-gray-200 sticky top-0 bg-gray-50/95 backdrop-blur z-20 pt-2">
                {[
                  { id: 'SUMMARY', label: '📊 摘要' },
                  { id: 'PERFORMANCE', label: '📈 績效分析' },
                  { id: 'LOGS', label: '📝 交易記錄' },
                  { id: 'OPTIMIZATION', label: '⚡ 參數優化' },
                  { id: 'BATCH', label: '🔄 批量優化' },
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as Tab)}
                    className={`px-6 py-3 text-sm font-medium transition-colors relative ${activeTab === tab.id
                      ? 'text-teal-600 border-b-2 border-teal-500 bg-teal-50/50'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                      }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div className="animate-fadeIn">
                {renderTabContent()}
              </div>

            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
