import React from 'react';
import type { BacktestResult, BacktestRequest } from '../../types/api';
import MetricsCard from '../MetricsCard';
import EquityChart from '../EquityChart';

interface SummaryTabProps {
  result: BacktestResult;
  request: BacktestRequest;
}

const SummaryTab: React.FC<SummaryTabProps> = ({ result, request }) => {
  return (
    <div className="space-y-6">
      {/* 淨值曲線圖 */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">淨值曲線圖</h3>
        <EquityChart
          data={result.equity_curve}
          buyHoldData={result.buy_hold_curve}
          trades={result.trades}
        />
      </div>

      {/* 績效指標 */}
      <MetricsCard result={result} request={request} />
    </div>
  );
};

export default SummaryTab;
