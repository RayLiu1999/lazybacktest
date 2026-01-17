import React from 'react';
import type { BacktestResult } from '../types/api';

interface MetricsCardProps {
  result: BacktestResult;
}

const MetricsCard: React.FC<MetricsCardProps> = ({ result }) => {
  const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;
  const formatCurrency = (value: number) => `$${value.toLocaleString()}`;

  const metrics = [
    {
      label: '總報酬率',
      value: formatPercent(result.total_return),
      positive: result.total_return >= 0,
      icon: result.total_return >= 0 ? '📈' : '📉',
    },
    {
      label: '年化報酬率 (CAGR)',
      value: formatPercent(result.cagr),
      positive: result.cagr >= 0,
      icon: '📊',
    },
    {
      label: '最大回撤 (MDD)',
      value: formatPercent(result.max_drawdown),
      positive: false,
      icon: '⚠️',
    },
    {
      label: '勝率',
      value: formatPercent(result.win_rate),
      positive: result.win_rate >= 0.5,
      icon: '🎯',
    },
    {
      label: '交易次數',
      value: result.total_trades.toString(),
      positive: true,
      neutral: true,
      icon: '🔄',
    },
    {
      label: '最終資金',
      value: formatCurrency(result.final_capital),
      positive: result.final_capital >= 100000,
      icon: '💰',
    },
  ];

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl p-6">
      <h3 className="text-cyan-400 text-lg font-semibold mb-6">📋 績效指標</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {metrics.map((metric) => (
          <div
            key={metric.label}
            className="flex items-center gap-3 p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all"
          >
            <span className="text-2xl">{metric.icon}</span>
            <div className="flex flex-col gap-1">
              <span className="text-xs text-slate-400">{metric.label}</span>
              <span
                className={`text-xl font-semibold ${'neutral' in metric && metric.neutral
                    ? 'text-blue-400'
                    : metric.positive
                      ? 'text-green-400'
                      : 'text-red-400'
                  }`}
              >
                {metric.value}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MetricsCard;
