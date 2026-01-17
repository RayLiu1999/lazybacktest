import React, { useState } from 'react';
import type { BacktestRequest } from '../types/api';
import BasicSettings from './forms/BasicSettings';
import TradingSettings from './forms/TradingSettings';
import RiskManagement from './forms/RiskManagement';
import StrategySettings from './forms/StrategySettings';

interface BacktestFormProps {
  onSubmit: (request: BacktestRequest) => void;
  isLoading: boolean;
}

const BacktestForm: React.FC<BacktestFormProps> = ({ onSubmit, isLoading }) => {
  const [request, setRequest] = useState<BacktestRequest>({
    ticker: '2330',
    start_date: '2024-01-01',
    end_date: '2024-12-31',
    initial_capital: 100000,
    trading_settings: {
      timing: 'N_CLOSE',
      buy_fee: 0.001425,
      sell_fee: 0.004425, // 含稅
      tax: 0.003
    },
    risk_settings: {
      position_basis: 'INITIAL_CAPITAL',
      position_pct: 100
    },
    strategy_settings: {
      entry_strategy: 'SMA_CROSS',
      entry_params: { short_period: 5, long_period: 20 },
      exit_strategy: 'SAME_AS_ENTRY',
      exit_params: {}
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(request);
  };

  const updateRequest = (updates: Partial<BacktestRequest>) => {
    setRequest(prev => ({ ...prev, ...updates }));
  };

  const updateTrading = (updates: Partial<typeof request.trading_settings>) => {
    setRequest(prev => ({
      ...prev,
      trading_settings: { ...prev.trading_settings, ...updates }
    }));
  };

  const updateRisk = (updates: Partial<typeof request.risk_settings>) => {
    setRequest(prev => ({
      ...prev,
      risk_settings: { ...prev.risk_settings, ...updates }
    }));
  };

  const updateStrategy = (updates: Partial<typeof request.strategy_settings>) => {
    setRequest(prev => ({
      ...prev,
      strategy_settings: { ...prev.strategy_settings, ...updates }
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">

      <BasicSettings request={request} onChange={updateRequest} />

      <TradingSettings settings={request.trading_settings} onChange={updateTrading} />

      <RiskManagement settings={request.risk_settings} onChange={updateRisk} />

      <StrategySettings settings={request.strategy_settings} onChange={updateStrategy} />

      {/* Action Buttons */}
      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          disabled={isLoading}
          className="flex-1 bg-teal-500 hover:bg-teal-600 text-white font-semibold py-3 px-6 rounded-xl shadow-sm transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>回測中...</span>
            </>
          ) : (
            <>
              <span>🚀</span>
              <span>開始回測</span>
            </>
          )}
        </button>

        <button
          type="button"
          className="px-4 py-3 bg-white border border-gray-300 text-gray-600 rounded-xl hover:bg-gray-50 transition-colors"
          title="重設參數"
          onClick={() => {/* Reset logic */ }}
        >
          ↺
        </button>
      </div>

    </form>
  );
};

export default BacktestForm;
