import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MetricsCard from '../../components/MetricsCard';
import type { BacktestResult } from '../../types/api';

const mockResult: BacktestResult = {
  ticker: '2330',
  total_return: 0.15,
  cagr: 0.12,
  max_drawdown: 0.08,
  win_rate: 0.65,
  total_trades: 10,
  final_capital: 115000,
  trades: [],
  equity_curve: [100000, 105000, 110000, 115000],
};

describe('MetricsCard', () => {
  describe('渲染測試', () => {
    it('應該渲染績效指標標題', () => {
      render(<MetricsCard result={mockResult} />);
      expect(screen.getByText(/績效指標/)).toBeInTheDocument();
    });

    it('應該顯示總報酬率', () => {
      render(<MetricsCard result={mockResult} />);
      expect(screen.getByText('總報酬率')).toBeInTheDocument();
      expect(screen.getByText('15.00%')).toBeInTheDocument();
    });

    it('應該顯示年化報酬率', () => {
      render(<MetricsCard result={mockResult} />);
      expect(screen.getByText('年化報酬率')).toBeInTheDocument();
      expect(screen.getByText('12.00%')).toBeInTheDocument();
    });

    it('應該顯示最大回撤', () => {
      render(<MetricsCard result={mockResult} />);
      expect(screen.getByText('最大回撤')).toBeInTheDocument();
      expect(screen.getByText('8.00%')).toBeInTheDocument();
    });

    it('應該顯示夏普比率 (Sharpe)', () => {
      render(<MetricsCard result={mockResult} />);
      expect(screen.getByText('夏普比率 (Sharpe)')).toBeInTheDocument();
    });

    it('應該顯示交易次數', () => {
      render(<MetricsCard result={mockResult} />);
      expect(screen.getByText('交易次數')).toBeInTheDocument();
      expect(screen.getByText('10')).toBeInTheDocument();
    });

    it('應該顯示最終資金', () => {
      render(<MetricsCard result={mockResult} />);
      expect(screen.getByText('最終資金')).toBeInTheDocument();
      expect(screen.getByText('$115,000')).toBeInTheDocument();
    });
  });

  describe('邊界情況', () => {
    it('應該正確處理負報酬率', () => {
      const negativeResult: BacktestResult = {
        ...mockResult,
        total_return: -0.1,
        final_capital: 90000,
      };
      render(<MetricsCard result={negativeResult} />);
      expect(screen.getByText('-10.00%')).toBeInTheDocument();
    });

    it('應該正確處理零交易次數', () => {
      const zeroTradesResult: BacktestResult = {
        ...mockResult,
        total_trades: 0,
        win_rate: 0,
      };
      render(<MetricsCard result={zeroTradesResult} />);
      expect(screen.getByText('0')).toBeInTheDocument();
    });
  });
});
