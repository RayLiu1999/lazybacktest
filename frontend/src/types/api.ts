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

// 策略參數值
export type StrategyParamValue = number | string;

// 策略設定
export interface StrategySettings {
  entry_strategy: string;
  entry_params: Record<string, StrategyParamValue>;
  exit_strategy: string;
  exit_params: Record<string, StrategyParamValue>;
}

// 交易設定
export interface TradingSettings {
  timing: 'N_CLOSE' | 'N1_OPEN';  // 匹配後端
  buy_fee: number;
  sell_fee: number;
  tax: number;
}

// 風險管理
export interface RiskSettings {
  position_basis: 'INITIAL_CAPITAL' | 'TOTAL_CAPITAL';
  position_pct: number;
  stop_loss?: number;  // 匹配後端欄位名
  take_profit?: number;
}

// 回測請求
export interface BacktestRequest {
  // 基本設定
  ticker: string;
  start_date: string;
  end_date: string;
  initial_capital: number;

  // 進階設定
  trading_settings: TradingSettings;
  risk_settings: RiskSettings;
  strategy_settings: StrategySettings;
}

// 交易記錄
export interface Trade {
  date: string;
  action: 'BUY' | 'SELL';
  price: number;
  quantity: number;
  profit?: number;
  strategy_params?: string; // 當時的策略參數快照
}

// 績效指標 (擴充)
export interface PerformanceMetrics {
  total_return: number;
  cagr: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  final_capital: number;
  sharpe_ratio?: number; // Phase 8
  sortino_ratio?: number; // Phase 8
  calmar_ratio?: number; // Phase 8
  best_trade?: number;
  worst_trade?: number;
  avg_profit?: number;
  avg_loss?: number;
}

// 回測結果
export interface BacktestResult extends PerformanceMetrics {
  ticker: string;
  trades: Trade[];
  equity_curve: { date: string; equity: number; return_pct: number; drawdown: number }[];
  buy_hold_curve?: { date: string; equity: number; return_pct: number }[];  // Phase 11: 雙線對照
  buy_hold_return?: number;  // Phase 8
  avg_trade_pnl?: number;  // Phase 11: 平均交易盈虧
  max_consecutive_wins?: number;  // Phase 11: 最大連勝
  max_consecutive_losses?: number;  // Phase 11: 最大連敗
  monthly_returns?: { year: number; month: number; return: number }[];
  yearly_returns?: Record<number, number>;  // { 2024: 0.15, 2025: 0.20 }
}

// 參數優化請求
export interface OptimizationRequest {
  ticker: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  entry_strategy: string;
  param_ranges: Record<string, number[]>;
}

// 參數優化結果
export interface OptimizationResult {
  ticker: string;
  strategy: string;
  results_count: number;
  results: {
    params: Record<string, number>;
    metrics: PerformanceMetrics;
  }[];
}
