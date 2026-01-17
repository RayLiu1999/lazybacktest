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
  timing: 'N_CLOSE' | 'N_PLUS_1_OPEN';
  buy_fee: number;
  sell_fee: number;
  tax: number;
}

// 風險管理
export interface RiskSettings {
  position_basis: 'INITIAL_CAPITAL' | 'TOTAL_CAPITAL';
  position_pct: number;
  stop_loss_pct?: number;
  take_profit_pct?: number;
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
  equity_curve: { date: string; equity: number; drawdown: number }[];
  monthly_returns?: { year: number; month: number; return: number }[]; // Phase 8 for heatmap
  yearly_returns?: { year: number; return: number }[]; // Phase 8 for bar chart
}
