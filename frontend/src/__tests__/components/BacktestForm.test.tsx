import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import BacktestForm from '../../components/BacktestForm';

describe('BacktestForm', () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  describe('渲染測試', () => {
    it('應該渲染表單標題', () => {
      render(<BacktestForm onSubmit={mockOnSubmit} isLoading={false} />);
      expect(screen.getByText(/回測設定/)).toBeInTheDocument();
    });

    it('應該渲染股票代碼輸入欄位', () => {
      render(<BacktestForm onSubmit={mockOnSubmit} isLoading={false} />);
      expect(screen.getByLabelText(/股票代號\/名稱/)).toBeInTheDocument();
    });

    it('應該渲染開始日期與結束日期欄位', () => {
      render(<BacktestForm onSubmit={mockOnSubmit} isLoading={false} />);
      expect(screen.getByLabelText(/開始日期/)).toBeInTheDocument();
      expect(screen.getByLabelText(/結束日期/)).toBeInTheDocument();
    });

    it('應該渲染初始資金欄位', () => {
      render(<BacktestForm onSubmit={mockOnSubmit} isLoading={false} />);
      expect(screen.getByLabelText(/初始資金/)).toBeInTheDocument();
    });

    it('應該渲染策略選擇欄位', () => {
      render(<BacktestForm onSubmit={mockOnSubmit} isLoading={false} />);
      expect(screen.getByLabelText(/進場策略/)).toBeInTheDocument();
    });

    it('應該渲染提交按鈕', () => {
      render(<BacktestForm onSubmit={mockOnSubmit} isLoading={false} />);
      expect(screen.getByRole('button', { name: /開始回測/ })).toBeInTheDocument();
    });
  });

  describe.skip('預設值測試', () => {
    it('股票代碼預設為 2330', () => {
      render(<BacktestForm onSubmit={mockOnSubmit} isLoading={false} />);
      const tickerInput = screen.getByLabelText(/股票代號\/名稱/) as HTMLInputElement;
      expect(tickerInput.value).toBe('2330');
    });

    it('初始資金預設為 100000', () => {
      render(<BacktestForm onSubmit={mockOnSubmit} isLoading={false} />);
      const capitalInput = screen.getByLabelText(/初始資金/) as HTMLInputElement;
      expect(capitalInput.value).toBe('100000');
    });
  });

  describe.skip('使用者互動測試', () => {
    it('應該能修改股票代碼', async () => {
      const user = userEvent.setup();
      render(<BacktestForm onSubmit={mockOnSubmit} isLoading={false} />);

      const tickerInput = screen.getByLabelText(/股票代號\/名稱/) as HTMLInputElement;
      await user.clear(tickerInput);
      await user.type(tickerInput, '2317');

      expect(tickerInput.value).toBe('2317');
    });

    it('應該能修改初始資金', async () => {
      const user = userEvent.setup();
      render(<BacktestForm onSubmit={mockOnSubmit} isLoading={false} />);

      const capitalInput = screen.getByLabelText(/初始資金/) as HTMLInputElement;
      await user.clear(capitalInput);
      await user.type(capitalInput, '500000');

      expect(capitalInput.value).toBe('500000');
    });
  });

  describe.skip('表單提交測試', () => {
    it('點擊提交按鈕應該呼叫 onSubmit', async () => {
      const user = userEvent.setup();
      render(<BacktestForm onSubmit={mockOnSubmit} isLoading={false} />);

      const submitButton = screen.getByRole('button', { name: /開始回測/ });
      await user.click(submitButton);

      expect(mockOnSubmit).toHaveBeenCalledTimes(1);
    });

    it('提交時應該傳遞正確的表單資料', async () => {
      const user = userEvent.setup();
      render(<BacktestForm onSubmit={mockOnSubmit} isLoading={false} />);

      const submitButton = screen.getByRole('button', { name: /開始回測/ });
      await user.click(submitButton);

      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          ticker: '2330',
          initial_capital: 100000,
          strategy_settings: expect.objectContaining({
            entry_strategy: 'SMA_CROSS',
          }),
        })
      );
    });
  });

  describe('載入狀態測試', () => {
    it('載入中時按鈕應該顯示「回測中...」', () => {
      render(<BacktestForm onSubmit={mockOnSubmit} isLoading={true} />);
      expect(screen.getByRole('button', { name: /回測中/ })).toBeInTheDocument();
    });

    it('載入中時按鈕應該被禁用', () => {
      render(<BacktestForm onSubmit={mockOnSubmit} isLoading={true} />);
      const button = screen.getByRole('button', { name: /回測中/ });
      expect(button).toBeDisabled();
    });
  });
});
