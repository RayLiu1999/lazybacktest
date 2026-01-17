/**
 * API 類型定義
 */

// 股價資料
export interface StockPrice {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// 策略配置
export interface StrategyConfig {
  name: string;
  params: Record<string, number>;
}

// 回測請求
export interface BacktestRequest {
  ticker: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  buy_fee?: number;
  sell_fee?: number;
  tax?: number;
  strategy: StrategyConfig;
}

// 交易記錄
export interface Trade {
  date: string;
  type: string;
  price: number;
  quantity: number;
  profit: number | null;
}

// 回測結果
export interface BacktestResult {
  ticker: string;
  total_return: number;
  cagr: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  final_capital: number;
  trades: Trade[];
  equity_curve: number[];
}
