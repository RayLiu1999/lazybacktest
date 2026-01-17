import React from 'react';
import type { BacktestResult } from '../types/api';
import './MetricsCard.css';

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
      color: result.total_return >= 0 ? '#4ade80' : '#f87171',
      icon: result.total_return >= 0 ? '📈' : '📉',
    },
    {
      label: '年化報酬率 (CAGR)',
      value: formatPercent(result.cagr),
      color: result.cagr >= 0 ? '#4ade80' : '#f87171',
      icon: '📊',
    },
    {
      label: '最大回撤 (MDD)',
      value: formatPercent(result.max_drawdown),
      color: '#f87171',
      icon: '⚠️',
    },
    {
      label: '勝率',
      value: formatPercent(result.win_rate),
      color: result.win_rate >= 0.5 ? '#4ade80' : '#fbbf24',
      icon: '🎯',
    },
    {
      label: '交易次數',
      value: result.total_trades.toString(),
      color: '#60a5fa',
      icon: '🔄',
    },
    {
      label: '最終資金',
      value: formatCurrency(result.final_capital),
      color: result.final_capital >= 100000 ? '#4ade80' : '#f87171',
      icon: '💰',
    },
  ];

  return (
    <div className="metrics-card">
      <h3>📋 績效指標</h3>
      <div className="metrics-grid">
        {metrics.map((metric) => (
          <div key={metric.label} className="metric-item">
            <span className="metric-icon">{metric.icon}</span>
            <div className="metric-content">
              <span className="metric-label">{metric.label}</span>
              <span className="metric-value" style={{ color: metric.color }}>
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
