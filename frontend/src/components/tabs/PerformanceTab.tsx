import React from 'react';

const PerformanceTab: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-yellow-800 text-sm">
        ⚠️ 進階績效分析功能目前尚在開發中 (Phase 8)，此畫面僅為預覽。
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm h-64 flex items-center justify-center bg-gray-50 border-dashed">
          <div className="text-center text-gray-400">
            <span className="text-4xl block mb-2">📊</span>
            <span className="text-sm">年度報酬柱狀圖 (待實作)</span>
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm h-64 flex items-center justify-center bg-gray-50 border-dashed">
          <div className="text-center text-gray-400">
            <span className="text-4xl block mb-2">📅</span>
            <span className="text-sm">月度報酬熱力圖 (待實作)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceTab;
