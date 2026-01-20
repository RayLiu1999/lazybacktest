import React from 'react';
import type { BacktestResult, BacktestRequest } from '../types/api';

interface MetricsCardProps {
  result: BacktestResult;
  request?: BacktestRequest;
}

const MetricsCard: React.FC<MetricsCardProps> = ({ result, request }) => {
  const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;
  const formatCurrency = (value: number) => {
    return value >= 0
      ? `+$${Math.round(value).toLocaleString()}`
      : `-$${Math.round(Math.abs(value)).toLocaleString()}`;
  };
  const formatNumber = (value: number) => value.toFixed(2);

  // Helper for metric item
  const MetricItem = ({ label, value, subLabel, colorClass = 'text-gray-800' }: { label: string, value: string, subLabel?: string, colorClass?: string }) => (
    <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex flex-col items-center justify-center text-center h-28">
      <div className="text-sm text-gray-500 mb-1 flex items-center gap-1">
        {label}
        <span className="text-gray-300 text-xs">?</span>
      </div>
      <div className={`text-2xl font-bold ${colorClass}`}>
        {value}
      </div>
      {subLabel && <div className="text-xs text-gray-400 mt-1">{subLabel}</div>}
    </div>
  );

  // Helper for setting item
  const SettingItem = ({ label, value, icon }: { label: string, value: string, icon: string }) => (
    <div className="bg-gray-50 p-4 rounded-xl flex flex-col items-center justify-center text-center h-24">
      <div className="text-xs text-gray-500 mb-1 flex items-center gap-1">
        <span>{icon}</span> {label}
      </div>
      <div className="font-semibold text-gray-800">
        {value}
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      {/* 1. 績效指標 */}
      <section>
        <h3 className="text-lg font-semibold text-gray-700 mb-4">績效指標</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricItem
            label="年化報酬率"
            value={formatPercent(result.cagr)}
            colorClass={result.cagr >= 0 ? 'text-teal-600' : 'text-red-500'}
          />
          <MetricItem
            label="買入持有年化"
            value={result.buy_hold_cagr !== undefined ? formatPercent(result.buy_hold_cagr) : '-'}
            colorClass={(result.buy_hold_cagr ?? 0) >= 0 ? 'text-teal-600' : 'text-red-500'}
          />
          <MetricItem
            label="總報酬率"
            value={formatPercent(result.total_return)}
            colorClass={result.total_return >= 0 ? 'text-teal-600' : 'text-red-500'}
          />
          <MetricItem
            label="Buy & Hold"
            value={result.buy_hold_return !== undefined ? formatPercent(result.buy_hold_return) : '-'}
            colorClass={(result.buy_hold_return ?? 0) >= 0 ? 'text-teal-600' : 'text-red-500'}
            subLabel="總報酬"
          />
        </div>
      </section>

      {/* 2. 風險指標 */}
      <section>
        <h3 className="text-lg font-semibold text-gray-700 mb-4">風險指標</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricItem
            label="最大回撤"
            value={formatPercent(result.max_drawdown)}
            colorClass="text-red-500"
          />
          <MetricItem
            label="夏普值"
            value={result.sharpe_ratio !== undefined ? formatNumber(result.sharpe_ratio) : '-'}
            colorClass="text-blue-600"
          />
          <MetricItem
            label="索提諾比率"
            value={result.sortino_ratio !== undefined ? formatNumber(result.sortino_ratio) : '-'}
            colorClass="text-gray-700"
          />
          <MetricItem
            label="過擬合(報酬率比)"
            value={result.overfitting_ratio?.return_ratio !== null && result.overfitting_ratio?.return_ratio !== undefined ? formatNumber(result.overfitting_ratio.return_ratio) : '-'}
            colorClass={(result.overfitting_ratio?.return_ratio ?? 0) >= 1 ? 'text-orange-500' : 'text-gray-600'}
          />
        </div>
      </section>

      {/* 3. 交易統計 */}
      <section>
        <h3 className="text-lg font-semibold text-gray-700 mb-4">交易統計</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricItem
            label="勝率"
            value={formatPercent(result.win_rate)}
            subLabel={`(${Math.round(result.total_trades * result.win_rate)}/${result.total_trades})`}
            colorClass="text-gray-800"
          />
          <MetricItem
            label="總交易次數"
            value={result.total_trades.toString()}
            subLabel="次"
            colorClass="text-gray-800"
          />
          <MetricItem
            label="平均交易盈虧"
            value={result.avg_trade_pnl !== undefined ? formatCurrency(result.avg_trade_pnl) : '-'}
            subLabel="元"
            colorClass={(result.avg_trade_pnl ?? 0) >= 0 ? 'text-teal-600' : 'text-red-500'}
          />
          <MetricItem
            label="最大連勝次數"
            value={result.max_consecutive_wins !== undefined ? result.max_consecutive_wins.toString() : '-'}
            subLabel="次"
            colorClass="text-gray-800"
          />
        </div>
      </section>

      {/* 4. 策略設定 */}
      <section>
        <h3 className="text-lg font-semibold text-gray-700 mb-4">策略設定</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <SettingItem
            label="進場策略"
            value={request?.strategy_settings.entry_strategy || '-'}
            icon="📈"
          />
          <SettingItem
            label="出場策略"
            value={request?.strategy_settings.exit_strategy || '-'}
            icon="📉"
          />
          <SettingItem
            label="做空策略未啟用"
            value="--"
            icon="🔄"
          />
          <SettingItem
            label="全局風控"
            value={`損:${request?.risk_settings.stop_loss || 'N/A'}% / 利:${request?.risk_settings.take_profit || 'N/A'}%`}
            icon="⚠️"
          />
          <SettingItem
            label="回補策略未啟用"
            value="--"
            icon="📈"
          />
          <SettingItem
            label="買賣時間點"
            value={request?.trading_settings.timing === 'N_CLOSE' ? '收盤價' : '隔日開盤'}
            icon="⏰"
          />
          <SettingItem
            label="初始本金"
            value={`$${(request?.initial_capital || 0).toLocaleString()}`}
            icon="💰"
          />
          <SettingItem
            label="最終資產"
            value={`$${result.final_capital.toLocaleString()}`}
            icon="🏆"
          />
        </div>
      </section>
    </div>
  );
};

export default MetricsCard;
