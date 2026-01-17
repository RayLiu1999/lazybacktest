import React, { useState } from 'react';
import type { BacktestRequest, StrategyConfig } from '../types/api';

interface BacktestFormProps {
  onSubmit: (request: BacktestRequest) => void;
  isLoading: boolean;
}

const BacktestForm: React.FC<BacktestFormProps> = ({ onSubmit, isLoading }) => {
  const [ticker, setTicker] = useState('2330');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [initialCapital, setInitialCapital] = useState(100000);
  const [strategyName, setStrategyName] = useState('sma_crossover');
  const [shortPeriod, setShortPeriod] = useState(5);
  const [longPeriod, setLongPeriod] = useState(20);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const strategy: StrategyConfig = {
      name: strategyName,
      params: {
        short_period: shortPeriod,
        long_period: longPeriod,
      },
    };

    const request: BacktestRequest = {
      ticker,
      start_date: startDate,
      end_date: endDate,
      initial_capital: initialCapital,
      strategy,
    };

    onSubmit(request);
  };

  const inputClass = "w-full px-4 py-3 bg-white/5 border border-white/15 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 transition-all";
  const labelClass = "block text-sm text-slate-400 mb-2";

  return (
    <form onSubmit={handleSubmit} className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl p-6 shadow-xl">
      <h2 className="text-xl font-semibold text-cyan-400 mb-6">📊 回測設定</h2>

      {/* 股票資訊 */}
      <div className="mb-6 pb-4 border-b border-white/10">
        <h3 className="text-xs uppercase tracking-wider text-slate-500 mb-4">股票資訊</h3>
        <div>
          <label htmlFor="ticker" className={labelClass}>股票代碼</label>
          <input
            id="ticker"
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            placeholder="例如: 2330"
            className={inputClass}
          />
        </div>
      </div>

      {/* 回測期間 */}
      <div className="mb-6 pb-4 border-b border-white/10">
        <h3 className="text-xs uppercase tracking-wider text-slate-500 mb-4">回測期間</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="startDate" className={labelClass}>開始日期</label>
            <input
              id="startDate"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className={inputClass}
            />
          </div>
          <div>
            <label htmlFor="endDate" className={labelClass}>結束日期</label>
            <input
              id="endDate"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className={inputClass}
            />
          </div>
        </div>
      </div>

      {/* 資金設定 */}
      <div className="mb-6 pb-4 border-b border-white/10">
        <h3 className="text-xs uppercase tracking-wider text-slate-500 mb-4">資金設定</h3>
        <div>
          <label htmlFor="capital" className={labelClass}>初始資金 (TWD)</label>
          <input
            id="capital"
            type="number"
            value={initialCapital}
            onChange={(e) => setInitialCapital(Number(e.target.value))}
            min={10000}
            step={10000}
            className={inputClass}
          />
        </div>
      </div>

      {/* 策略設定 */}
      <div className="mb-6">
        <h3 className="text-xs uppercase tracking-wider text-slate-500 mb-4">策略設定</h3>
        <div className="mb-4">
          <label htmlFor="strategy" className={labelClass}>策略類型</label>
          <select
            id="strategy"
            value={strategyName}
            onChange={(e) => setStrategyName(e.target.value)}
            className={inputClass}
          >
            <option value="sma_crossover">SMA 均線交叉</option>
          </select>
        </div>

        {strategyName === 'sma_crossover' && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="shortPeriod" className={labelClass}>短期均線 (日)</label>
              <input
                id="shortPeriod"
                type="number"
                value={shortPeriod}
                onChange={(e) => setShortPeriod(Number(e.target.value))}
                min={1}
                max={50}
                className={inputClass}
              />
            </div>
            <div>
              <label htmlFor="longPeriod" className={labelClass}>長期均線 (日)</label>
              <input
                id="longPeriod"
                type="number"
                value={longPeriod}
                onChange={(e) => setLongPeriod(Number(e.target.value))}
                min={5}
                max={200}
                className={inputClass}
              />
            </div>
          </div>
        )}
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-4 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg text-slate-900 font-semibold text-lg hover:from-cyan-400 hover:to-blue-400 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-cyan-500/25 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 transition-all"
      >
        {isLoading ? '執行中...' : '🚀 開始回測'}
      </button>
    </form>
  );
};

export default BacktestForm;
