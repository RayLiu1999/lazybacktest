import React from 'react';
import type { BacktestRequest } from '../../types/api';

interface BasicSettingsProps {
  request: BacktestRequest;
  onChange: (updates: Partial<BacktestRequest>) => void;
}

const BasicSettings: React.FC<BasicSettingsProps> = ({ request, onChange }) => {
  const handleDateShortcut = (years: number) => {
    const end = new Date();
    const start = new Date();
    start.setFullYear(end.getFullYear() - years);

    onChange({
      start_date: start.toISOString().split('T')[0],
      end_date: end.toISOString().split('T')[0],
    });
  };

  return (
    <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <span className="text-xl">⚙️</span>
        基本設定
      </h3>

      <div className="space-y-4">
        {/* 股票代號 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            股票代號/名稱
          </label>
          <input
            type="text"
            value={request.ticker}
            onChange={(e) => onChange({ ticker: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-all"
            placeholder="例如：2330"
          />
        </div>

        {/* 日期區間 */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              開始日期
            </label>
            <input
              type="date"
              value={request.start_date}
              onChange={(e) => onChange({ start_date: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-all"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              結束日期
            </label>
            <input
              type="date"
              value={request.end_date}
              onChange={(e) => onChange({ end_date: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-all"
            />
          </div>
        </div>

        {/* 日期捷徑 */}
        <div className="flex gap-2">
          {[1, 3, 5, 10].map((year) => (
            <button
              key={year}
              type="button"
              onClick={() => handleDateShortcut(year)}
              className="px-3 py-1 text-xs font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
            >
              近 {year} 年
            </button>
          ))}
        </div>

        {/* 初始資金 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            初始資金 ($)
          </label>
          <input
            type="number"
            value={request.initial_capital}
            onChange={(e) => onChange({ initial_capital: Number(e.target.value) })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-all"
          />
        </div>
      </div>
    </div>
  );
};

export default BasicSettings;
