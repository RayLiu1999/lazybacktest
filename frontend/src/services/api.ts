import axios from 'axios';
import type { BacktestRequest, BacktestResult, StockPrice, OptimizationRequest, OptimizationResult } from '../types/api';

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
 * 執行回測 (Phase 9: 使用新版 schema)
 */
export const runBacktest = async (request: BacktestRequest): Promise<BacktestResult> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/backtest/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Backtest failed');
  }

  return response.json();
};

/**
 * 執行參數優化 (Phase 8)
 */
export const runOptimization = async (request: OptimizationRequest): Promise<OptimizationResult> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/backtest/optimize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Optimization failed');
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
