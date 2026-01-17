import axios from 'axios';
import type { BacktestRequest, BacktestResult, StockPrice } from '../types/api';

// In Docker: use relative path (Nginx proxies /api to backend)
// In local dev: use localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_URL || (
  import.meta.env.PROD ? '' : 'http://localhost:8000'
);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 取得股票歷史資料
 */
export const getStockHistory = async (
  ticker: string,
  startDate: string,
  endDate: string
): Promise<StockPrice[]> => {
  const response = await api.get<StockPrice[]>(
    `/api/v1/stocks/${ticker}/history`,
    {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
    }
  );
  return response.data;
};

/**
 * 執行回測
 */
export const runBacktest = async (request: BacktestRequest): Promise<BacktestResult> => {
  // Temporary mapping: Convert complex request to simple backend request
  // Backend currently only accepts { ticker, start_date, end_date, initial_capital, strategy: { name, params } }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const backendPayload: any = {
    ticker: request.ticker,
    start_date: request.start_date,
    end_date: request.end_date,
    initial_capital: request.initial_capital,
    buy_fee: request.trading_settings.buy_fee,
    sell_fee: request.trading_settings.sell_fee,
    tax: request.trading_settings.tax,
    strategy: {
      name: request.strategy_settings.entry_strategy.toLowerCase(),
      params: request.strategy_settings.entry_params
    }
  };

  const response = await fetch(`${API_BASE_URL}/backtest/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(backendPayload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Backtest failed');
  }

  return response.json();
};

/**
 * 健康檢查
 */
export const healthCheck = async (): Promise<{ status: string; version: string }> => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
