import React from 'react';
import type { BacktestResult } from '../types/api';

interface MetricsCardProps {
  result: BacktestResult;
}

const MetricsCard: React.FC<MetricsCardProps> = ({ result }) => {
  const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;
  const formatCurrency = (value: number) => `$${Math.round(value).toLocaleString()}`;

  const metrics = [
    { label: '總報酬率', value: formatPercent(result.total_return), positive: result.total_return >= 0 },
    { label: 'Buy & Hold', value: result.buy_hold_return !== undefined ? formatPercent(result.buy_hold_return) : '-', positive: (result.buy_hold_return ?? 0) >= 0 },
    { label: '年化報酬率 (CAGR)', value: formatPercent(result.cagr), positive: result.cagr >= 0 },
    { label: '最大回撤 (MDD)', value: formatPercent(result.max_drawdown), positive: false },
    { label: '夏普比率', value: result.sharpe_ratio !== undefined ? result.sharpe_ratio.toFixed(2) : '-', positive: (result.sharpe_ratio ?? 0) > 0 },
    { label: '索提諾比率', value: result.sortino_ratio !== undefined ? result.sortino_ratio.toFixed(2) : '-', positive: (result.sortino_ratio ?? 0) > 0 },
    { label: '勝率', value: formatPercent(result.win_rate), positive: result.win_rate >= 0.5 },
    { label: '交易次數', value: result.total_trades.toString(), neutral: true },
    { label: '平均交易盈虧', value: result.avg_trade_pnl !== undefined ? formatCurrency(result.avg_trade_pnl) : '-', positive: (result.avg_trade_pnl ?? 0) >= 0 },
    { label: '最大連勝', value: result.max_consecutive_wins !== undefined ? `${result.max_consecutive_wins}次` : '-', neutral: true },
    { label: '最大連敗', value: result.max_consecutive_losses !== undefined ? `${result.max_consecutive_losses}次` : '-', neutral: true },
    { label: '最終資金', value: formatCurrency(result.final_capital), positive: result.final_capital >= 100000 },
  ];

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h3 className="text-lg font-semibold text-gray-800">績效指標</h3>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-px bg-gray-200">
        {metrics.map((metric) => (
          <div key={metric.label} className="bg-white p-4">
            <div className="text-xs text-gray-500 mb-1">{metric.label}</div>
            <div className={`text-xl font-bold ${metric.neutral ? 'text-gray-800' :
              metric.positive ? 'text-green-600' : 'text-red-600'
              }`}>
              {metric.value}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MetricsCard;
