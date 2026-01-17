import React from 'react';

const OptimizationTab: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-yellow-800 text-sm">
        ⚠️ 參數優化功能目前尚在開發中 (Phase 8)，此畫面僅為預覽。
      </div>

      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">參數範圍設定</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-700">短均線週期 (Short Period)</h4>
            <div className="flex items-center gap-3">
              <input type="number" placeholder="Min" defaultValue={3} className="w-full px-3 py-2 border rounded-lg text-sm" />
              <span className="text-gray-400">-</span>
              <input type="number" placeholder="Max" defaultValue={10} className="w-full px-3 py-2 border rounded-lg text-sm" />
              <span className="text-gray-400">Step</span>
              <input type="number" placeholder="1" defaultValue={1} className="w-20 px-3 py-2 border rounded-lg text-sm" />
            </div>
          </div>
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-700">長均線週期 (Long Period)</h4>
            <div className="flex items-center gap-3">
              <input type="number" placeholder="Min" defaultValue={10} className="w-full px-3 py-2 border rounded-lg text-sm" />
              <span className="text-gray-400">-</span>
              <input type="number" placeholder="Max" defaultValue={50} className="w-full px-3 py-2 border rounded-lg text-sm" />
              <span className="text-gray-400">Step</span>
              <input type="number" placeholder="5" defaultValue={5} className="w-20 px-3 py-2 border rounded-lg text-sm" />
            </div>
          </div>
        </div>
        <div className="mt-6 flex justify-end">
          <button disabled className="px-6 py-2 bg-gray-200 text-gray-500 rounded-lg font-medium cursor-not-allowed">
            開始優化
          </button>
        </div>
      </div>

      {/* Mock Result Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden opacity-60">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h3 className="text-lg font-semibold text-gray-800">優化結果 (範例)</h3>
        </div>
        <table className="w-full text-left">
          <thead>
            <tr className="bg-gray-50 text-gray-600 text-sm">
              <th className="px-6 py-3">參數組合</th>
              <th className="px-6 py-3 text-right">總報酬率</th>
              <th className="px-6 py-3 text-right">Sharpe</th>
              <th className="px-6 py-3 text-right">MDD</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 text-sm">
            <tr>
              <td className="px-6 py-3">5, 20</td>
              <td className="px-6 py-3 text-right text-green-600">15.4%</td>
              <td className="px-6 py-3 text-right">1.25</td>
              <td className="px-6 py-3 text-right text-red-600">-10.5%</td>
            </tr>
            <tr>
              <td className="px-6 py-3">10, 60</td>
              <td className="px-6 py-3 text-right text-green-600">12.1%</td>
              <td className="px-6 py-3 text-right">0.98</td>
              <td className="px-6 py-3 text-right text-red-600">-8.2%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default OptimizationTab;
