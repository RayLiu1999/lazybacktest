import React from 'react';
import type { BacktestResult } from '../../types/api';

interface TradeLogsTabProps {
  result: BacktestResult;
}

const TradeLogsTab: React.FC<TradeLogsTabProps> = ({ result }) => {
  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-800">交易記錄</h3>
        <button className="px-3 py-1.5 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
          匯出 CSV
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 text-gray-600 text-sm border-b border-gray-200">
              <th className="px-6 py-3 font-medium">日期</th>
              <th className="px-6 py-3 font-medium">動作</th>
              <th className="px-6 py-3 font-medium text-right">價格</th>
              <th className="px-6 py-3 font-medium text-right">股數</th>
              <th className="px-6 py-3 font-medium text-right">損益</th>
              <th className="px-6 py-3 font-medium">策略紀錄</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {result.trades.map((trade, index) => (
              <tr key={index} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 text-sm text-gray-600 font-mono">
                  {trade.date}
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${trade.action === 'BUY'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                    }`}>
                    {trade.action === 'BUY' ? '買入' : '賣出'}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600 text-right font-mono">
                  ${trade.price.toFixed(2)}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600 text-right font-mono">
                  {trade.quantity.toLocaleString()}
                </td>
                <td className="px-6 py-4 text-right font-mono text-sm">
                  {trade.profit !== undefined && trade.profit !== null ? (
                    <span className={trade.profit >= 0 ? 'text-green-600 font-bold' : 'text-red-600 font-bold'}>
                      {trade.profit > 0 ? '+' : ''}{trade.profit.toFixed(0)}
                    </span>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </td>
                <td className="px-6 py-4 text-xs text-gray-500 max-w-xs truncate">
                  {trade.strategy_params || '-'}
                </td>
              </tr>
            ))}
            {result.trades.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                  尚無交易記錄
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TradeLogsTab;
