import React, { useState } from 'react';
import type { BacktestRequest, StrategyConfig } from '../types/api';

interface BacktestFormProps {
  onSubmit: (request: BacktestRequest) => void;
  isLoading: boolean;
}

const BacktestForm: React.FC<BacktestFormProps> = ({ onSubmit, isLoading }) => {
  const [ticker, setTicker] = useState('2330');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [initialCapital, setInitialCapital] = useState(100000);
  const [shortPeriod, setShortPeriod] = useState(5);
  const [longPeriod, setLongPeriod] = useState(20);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (shortPeriod >= longPeriod) {
      alert('短期均線必須小於長期均線');
      return;
    }

    const strategy: StrategyConfig = {
      name: 'sma_crossover',
      params: { short_period: shortPeriod, long_period: longPeriod },
    };

    const request: BacktestRequest = {
      ticker,
      start_date: startDate,
      end_date: endDate,
      initial_capital: initialCapital,
      strategy,
    };

    onSubmit(request);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* 基本設定 */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
          <h3 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
            <span>⚙️</span> 基本設定
          </h3>
          <p className="text-xs text-gray-500 mt-0.5">設定要回測的股票和期間</p>
        </div>
        <div className="p-4 space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">股票代碼/名稱</label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="2330"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">開始日期</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">結束日期</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">初始資金 (台)</label>
            <input
              type="number"
              value={initialCapital}
              onChange={(e) => setInitialCapital(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* 策略設定 */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
          <h3 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
            <span>📈</span> 策略設定
          </h3>
          <p className="text-xs text-gray-500 mt-0.5">SMA 均線交叉策略</p>
        </div>
        <div className="p-4 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">短期 (日)</label>
              <input
                type="number"
                value={shortPeriod}
                onChange={(e) => setShortPeriod(Number(e.target.value))}
                min={1}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm text-center focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">長期 (日)</label>
              <input
                type="number"
                value={longPeriod}
                onChange={(e) => setLongPeriod(Number(e.target.value))}
                min={5}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm text-center focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-teal-500 hover:bg-teal-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        {isLoading ? (
          <>
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            執行中...
          </>
        ) : (
          <>
            🚀 開始回測
          </>
        )}
      </button>
    </form>
  );
};

export default BacktestForm;
