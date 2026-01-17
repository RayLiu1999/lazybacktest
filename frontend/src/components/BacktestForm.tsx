import React, { useState } from 'react';
import type { BacktestRequest, StrategyConfig } from '../types/api';
import './BacktestForm.css';

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

  return (
    <form className="backtest-form" onSubmit={handleSubmit}>
      <h2>📊 回測設定</h2>

      <div className="form-section">
        <h3>股票資訊</h3>
        <div className="form-group">
          <label htmlFor="ticker">股票代碼</label>
          <input
            id="ticker"
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            placeholder="例如: 2330"
          />
        </div>
      </div>

      <div className="form-section">
        <h3>回測期間</h3>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="startDate">開始日期</label>
            <input
              id="startDate"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="endDate">結束日期</label>
            <input
              id="endDate"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>資金設定</h3>
        <div className="form-group">
          <label htmlFor="capital">初始資金 (TWD)</label>
          <input
            id="capital"
            type="number"
            value={initialCapital}
            onChange={(e) => setInitialCapital(Number(e.target.value))}
            min={10000}
            step={10000}
          />
        </div>
      </div>

      <div className="form-section">
        <h3>策略設定</h3>
        <div className="form-group">
          <label htmlFor="strategy">策略類型</label>
          <select
            id="strategy"
            value={strategyName}
            onChange={(e) => setStrategyName(e.target.value)}
          >
            <option value="sma_crossover">SMA 均線交叉</option>
          </select>
        </div>

        {strategyName === 'sma_crossover' && (
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="shortPeriod">短期均線 (日)</label>
              <input
                id="shortPeriod"
                type="number"
                value={shortPeriod}
                onChange={(e) => setShortPeriod(Number(e.target.value))}
                min={1}
                max={50}
              />
            </div>
            <div className="form-group">
              <label htmlFor="longPeriod">長期均線 (日)</label>
              <input
                id="longPeriod"
                type="number"
                value={longPeriod}
                onChange={(e) => setLongPeriod(Number(e.target.value))}
                min={5}
                max={200}
              />
            </div>
          </div>
        )}
      </div>

      <button type="submit" className="submit-btn" disabled={isLoading}>
        {isLoading ? '執行中...' : '🚀 開始回測'}
      </button>
    </form>
  );
};

export default BacktestForm;
