import React, { useState } from 'react';
import { runOptimization } from '../../services/api';
import type { OptimizationResult } from '../../types/api';

interface OptimizationTabProps {
  ticker: string;
  startDate: string;
  endDate: string;
  initialCapital: number;
}

interface ParamRange {
  min: number;
  max: number;
  step: number;
}

const OptimizationTab: React.FC<OptimizationTabProps> = ({
  ticker,
  startDate,
  endDate,
  initialCapital
}) => {
  const [shortPeriod, setShortPeriod] = useState<ParamRange>({ min: 3, max: 10, step: 1 });
  const [longPeriod, setLongPeriod] = useState<ParamRange>({ min: 10, max: 50, step: 5 });
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 產生參數陣列
  const generateRange = (range: ParamRange): number[] => {
    const values: number[] = [];
    for (let i = range.min; i <= range.max; i += range.step) {
      values.push(i);
    }
    return values;
  };

  const handleOptimize = async () => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await runOptimization({
        ticker,
        start_date: startDate,
        end_date: endDate,
        initial_capital: initialCapital,
        entry_strategy: 'SMA_CROSS',
        param_ranges: {
          short_period: generateRange(shortPeriod),
          long_period: generateRange(longPeriod),
        }
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '優化失敗');
    } finally {
      setIsLoading(false);
    }
  };

  const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;

  return (
    <div className="space-y-6">
      {/* 參數範圍設定 */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">⚡ 參數範圍設定 (Grid Search)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-700">短均線週期 (Short Period)</h4>
            <div className="flex items-center gap-3">
              <input
                type="number"
                value={shortPeriod.min}
                onChange={(e) => setShortPeriod({ ...shortPeriod, min: Number(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg text-sm"
                placeholder="Min"
              />
              <span className="text-gray-400">-</span>
              <input
                type="number"
                value={shortPeriod.max}
                onChange={(e) => setShortPeriod({ ...shortPeriod, max: Number(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg text-sm"
                placeholder="Max"
              />
              <span className="text-gray-400">Step</span>
              <input
                type="number"
                value={shortPeriod.step}
                onChange={(e) => setShortPeriod({ ...shortPeriod, step: Number(e.target.value) })}
                className="w-20 px-3 py-2 border rounded-lg text-sm"
              />
            </div>
          </div>
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-700">長均線週期 (Long Period)</h4>
            <div className="flex items-center gap-3">
              <input
                type="number"
                value={longPeriod.min}
                onChange={(e) => setLongPeriod({ ...longPeriod, min: Number(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg text-sm"
                placeholder="Min"
              />
              <span className="text-gray-400">-</span>
              <input
                type="number"
                value={longPeriod.max}
                onChange={(e) => setLongPeriod({ ...longPeriod, max: Number(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg text-sm"
                placeholder="Max"
              />
              <span className="text-gray-400">Step</span>
              <input
                type="number"
                value={longPeriod.step}
                onChange={(e) => setLongPeriod({ ...longPeriod, step: Number(e.target.value) })}
                className="w-20 px-3 py-2 border rounded-lg text-sm"
              />
            </div>
          </div>
        </div>

        <div className="mt-4 text-sm text-gray-500">
          將測試 {generateRange(shortPeriod).length} × {generateRange(longPeriod).length} = {generateRange(shortPeriod).length * generateRange(longPeriod).length} 種參數組合
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={handleOptimize}
            disabled={isLoading}
            className={`px-6 py-2 rounded-lg font-medium transition-colors ${isLoading
                ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                : 'bg-teal-500 text-white hover:bg-teal-600'
              }`}
          >
            {isLoading ? '優化中...' : '開始優化'}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Results Table */}
      {result && result.results.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-800">優化結果 (依 Sharpe 排序)</h3>
            <span className="text-sm text-gray-500">共 {result.results.length} 種組合</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-gray-50 text-gray-600 text-sm">
                  <th className="px-6 py-3">#</th>
                  <th className="px-6 py-3">Short</th>
                  <th className="px-6 py-3">Long</th>
                  <th className="px-6 py-3 text-right">總報酬率</th>
                  <th className="px-6 py-3 text-right">Sharpe</th>
                  <th className="px-6 py-3 text-right">MDD</th>
                  <th className="px-6 py-3 text-right">交易次數</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-sm">
                {result.results.slice(0, 20).map((r, idx) => (
                  <tr key={idx} className={idx === 0 ? 'bg-teal-50' : ''}>
                    <td className="px-6 py-3 font-medium">{idx + 1}</td>
                    <td className="px-6 py-3">{r.params.short_period}</td>
                    <td className="px-6 py-3">{r.params.long_period}</td>
                    <td className={`px-6 py-3 text-right ${r.metrics.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatPercent(r.metrics.total_return)}
                    </td>
                    <td className="px-6 py-3 text-right font-medium">
                      {r.metrics.sharpe_ratio?.toFixed(2) ?? '-'}
                    </td>
                    <td className="px-6 py-3 text-right text-red-600">
                      {formatPercent(r.metrics.max_drawdown)}
                    </td>
                    <td className="px-6 py-3 text-right">{r.metrics.total_trades}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {result.results.length > 20 && (
            <div className="px-6 py-3 text-sm text-gray-500 border-t">
              顯示前 20 筆 / 共 {result.results.length} 筆結果
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default OptimizationTab;
