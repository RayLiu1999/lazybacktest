import React from 'react';
import type { PeriodPerformance } from '../types/api';

interface PeriodPerformanceTableProps {
  data: PeriodPerformance[];
}

const PeriodPerformanceTable: React.FC<PeriodPerformanceTableProps> = ({ data }) => {
  const formatPercent = (value: number | null) => {
    if (value === null) return '-';
    return `${(value * 100).toFixed(2)}%`;
  };

  const formatNumber = (value: number) => {
    return value.toFixed(2);
  };

  const getColorClass = (value: number | null) => {
    if (value === null) return 'text-gray-500';
    return value >= 0 ? 'text-green-600' : 'text-red-600';
  };

  if (!data || data.length === 0) {
    return <div className="text-gray-500 text-center py-4">無期間績效資料</div>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50">
            <th className="px-4 py-3 text-left font-medium text-gray-600">期間</th>
            <th className="px-4 py-3 text-right font-medium text-gray-600">策略累積報酬</th>
            <th className="px-4 py-3 text-right font-medium text-gray-600">買入持有累積報酬</th>
            <th className="px-4 py-3 text-right font-medium text-gray-600">夏普值</th>
            <th className="px-4 py-3 text-right font-medium text-gray-600">索提諾比率</th>
            <th className="px-4 py-3 text-right font-medium text-gray-600">最大回撤</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr
              key={row.period}
              className={`border-b border-gray-100 ${index === data.length - 1 ? 'bg-blue-50 font-medium' : 'hover:bg-gray-50'}`}
            >
              <td className="px-4 py-3 text-gray-800 font-medium">{row.period}</td>
              <td className={`px-4 py-3 text-right ${getColorClass(row.strategy_return)}`}>
                {formatPercent(row.strategy_return)}
              </td>
              <td className={`px-4 py-3 text-right ${getColorClass(row.buy_hold_return)}`}>
                {formatPercent(row.buy_hold_return)}
              </td>
              <td className={`px-4 py-3 text-right ${getColorClass(row.sharpe_ratio)}`}>
                {formatNumber(row.sharpe_ratio)}
              </td>
              <td className={`px-4 py-3 text-right ${getColorClass(row.sortino_ratio)}`}>
                {formatNumber(row.sortino_ratio)}
              </td>
              <td className="px-4 py-3 text-right text-red-600">
                {formatPercent(row.max_drawdown)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PeriodPerformanceTable;
