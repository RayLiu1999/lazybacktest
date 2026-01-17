import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { BacktestRequest, BacktestResult, StockPrice } from '../../types/api';

// 模擬 axios 模組
const mockGet = vi.fn();
const mockPost = vi.fn();

vi.mock('axios', () => ({
  default: {
    create: () => ({
      get: mockGet,
      post: mockPost,
    }),
  },
}));

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getStockHistory', () => {
    it('應該返回股價資料', async () => {
      const mockData: StockPrice[] = [
        { date: '2024-01-01', open: 100, high: 105, low: 99, close: 103, volume: 10000 },
        { date: '2024-01-02', open: 103, high: 108, low: 102, close: 106, volume: 12000 },
      ];
      mockGet.mockResolvedValueOnce({ data: mockData });

      // 動態 import 來獲取已 mock 的模組
      const { getStockHistory } = await import('../../services/api');
      const result = await getStockHistory('2330', '2024-01-01', '2024-01-02');

      expect(mockGet).toHaveBeenCalledWith(
        '/api/v1/stocks/2330/history',
        expect.objectContaining({
          params: { start_date: '2024-01-01', end_date: '2024-01-02' },
        })
      );
      expect(result).toHaveLength(2);
      expect(result[0].close).toBe(103);
    });
  });

  describe('runBacktest', () => {
    it('應該發送 POST 請求並返回回測結果', async () => {
      const mockResult: BacktestResult = {
        ticker: '2330',
        total_return: 0.15,
        cagr: 0.12,
        max_drawdown: 0.08,
        win_rate: 0.65,
        total_trades: 10,
        final_capital: 115000,
        trades: [],
        equity_curve: [{ date: '2024-01-01', equity: 100000, drawdown: 0 }, { date: '2024-12-31', equity: 115000, drawdown: 0 }],
      };
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (mockPost as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResult
      });
      // Mock global fetch for runBacktest which uses fetch
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockResult
      });

      const { runBacktest } = await import('../../services/api');
      const request: BacktestRequest = {
        ticker: '2330',
        start_date: '2024-01-01',
        end_date: '2024-12-31',
        initial_capital: 100000,
        trading_settings: {
          timing: 'N_CLOSE',
          buy_fee: 0.001425,
          sell_fee: 0.004425,
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
      };

      const result = await runBacktest(request);

      // Verify fetch call arguments for transformed payload
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/backtest/run'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('"ticker":"2330"')
        })
      );
      expect(result.total_return).toBe(0.15);
      expect(result.final_capital).toBe(115000);
    });
  });

  describe('healthCheck', () => {
    it('應該返回健康狀態', async () => {
      const mockHealth = { status: 'ok', version: '0.1.0' };
      mockGet.mockResolvedValueOnce({ data: mockHealth });

      const { healthCheck } = await import('../../services/api');
      const result = await healthCheck();

      expect(mockGet).toHaveBeenCalledWith('/health');
      expect(result.status).toBe('ok');
    });
  });

  describe('錯誤處理', () => {
    it('API 錯誤應該拋出異常', async () => {
      mockGet.mockRejectedValueOnce(new Error('Network Error'));

      const { getStockHistory } = await import('../../services/api');
      await expect(getStockHistory('2330', '2024-01-01', '2024-01-02')).rejects.toThrow('Network Error');
    });
  });
});
