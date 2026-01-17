import axios from 'axios';
import type { BacktestRequest, BacktestResult, StockPrice } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
export const runBacktest = async (
  request: BacktestRequest
): Promise<BacktestResult> => {
  const response = await api.post<BacktestResult>(
    '/api/v1/backtest/run',
    request
  );
  return response.data;
};

/**
 * 健康檢查
 */
export const healthCheck = async (): Promise<{ status: string; version: string }> => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
