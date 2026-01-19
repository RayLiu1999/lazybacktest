import React from 'react';
import type { BacktestResult } from '../../types/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import PeriodPerformanceTable from '../PeriodPerformanceTable';

interface PerformanceTabProps {
  result: BacktestResult;
}

const PerformanceTab: React.FC<PerformanceTabProps> = ({ result }) => {
  // 將 yearly_returns 物件轉換為陣列
  const yearlyData = result.yearly_returns
    ? Object.entries(result.yearly_returns).map(([year, value]) => ({
      year: parseInt(year),
      return: value * 100, // 轉為百分比
    }))
    : [];

  // 月度報酬表格資料
  const monthlyData = result.monthly_returns || [];
  const monthNames = ['', '1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];

  // 依年份分組月度資料
  const years = [...new Set(monthlyData.map(m => m.year))].sort();

  return (
    <div className="space-y-6">
      {/* 期間績效表 (Phase 11 P1) */}
      {result.period_performance && result.period_performance.length > 0 && (
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">📊 期間績效分析</h3>
          <PeriodPerformanceTable data={result.period_performance} />
        </div>
      )}

      {/* 年度報酬柱狀圖 */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">📊 年度報酬</h3>
        {yearlyData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={yearlyData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis tickFormatter={(v) => `${v.toFixed(0)}%`} />
              <Tooltip formatter={(value) => [`${Number(value).toFixed(2)}%`, '報酬率']} />
              <Bar dataKey="return" name="報酬率">
                {yearlyData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.return >= 0 ? '#10b981' : '#ef4444'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center text-gray-400 py-8">暫無年度報酬資料</div>
        )}
      </div>

      {/* 月度報酬表格 */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">📅 月度報酬</h3>
        {monthlyData.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-3 py-2 text-left">年份</th>
                  {monthNames.slice(1).map((m) => (
                    <th key={m} className="px-3 py-2 text-center">{m}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {years.map((year) => (
                  <tr key={year} className="border-t">
                    <td className="px-3 py-2 font-medium">{year}</td>
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((month) => {
                      const data = monthlyData.find(m => m.year === year && m.month === month);
                      const value = data?.return;
                      return (
                        <td key={month} className={`px-3 py-2 text-center ${value === undefined ? 'text-gray-300' :
                          value >= 0 ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'
                          }`}>
                          {value !== undefined ? `${(value * 100).toFixed(1)}%` : '-'}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center text-gray-400 py-8">暫無月度報酬資料</div>
        )}
      </div>
    </div>
  );
};

export default PerformanceTab;
