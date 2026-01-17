import React from 'react';
import type { StrategySettings as IStrategySettings, StrategyParamValue } from '../../types/api';

interface StrategySettingsProps {
  settings: IStrategySettings;
  onChange: (updates: Partial<IStrategySettings>) => void;
}

// 策略選項清單
const STRATEGY_OPTIONS = [
  { value: 'SMA_CROSS', label: 'SMA 黃金交叉' },
  { value: 'SMA_DEATH_CROSS', label: 'SMA 死亡交叉' },
  { value: 'PRICE_CROSS_SMA', label: '價格突破 SMA' },
  { value: 'RSI_OVERSOLD', label: 'RSI 超賣' },
  { value: 'RSI_OVERBOUGHT', label: 'RSI 超買' },
  { value: 'MACD_CROSS_UP', label: 'MACD 黃金交叉' },
  { value: 'MACD_CROSS_DOWN', label: 'MACD 死亡交叉' },
  { value: 'KD_CROSS_UP', label: 'KD 黃金交叉' },
  { value: 'KD_CROSS_DOWN', label: 'KD 死亡交叉' },
  { value: 'BOLLINGER_BREAKOUT', label: '布林通道突破' },
  { value: 'BOLLINGER_REVERSAL', label: '布林通道回歸' },
  { value: 'PRICE_BREAKOUT_HIGH', label: '價格突破近期高點' },
  { value: 'TURTLE_BREAKOUT', label: '海龜通道突破' },
];

// 策略參數定義 map
const STRATEGY_PARAM_DEFINITIONS: Record<string, Array<{ key: string; label: string; type: 'number'; default: number }>> = {
  SMA_CROSS: [
    { key: 'short_period', label: '短均線週期', type: 'number', default: 5 },
    { key: 'long_period', label: '長均線週期', type: 'number', default: 20 },
  ],
  SMA_DEATH_CROSS: [
    { key: 'short_period', label: '短均線週期', type: 'number', default: 5 },
    { key: 'long_period', label: '長均線週期', type: 'number', default: 20 },
  ],
  PRICE_CROSS_SMA: [
    { key: 'period', label: '均線週期', type: 'number', default: 20 },
  ],
  RSI_OVERSOLD: [
    { key: 'period', label: 'RSI 週期', type: 'number', default: 14 },
    { key: 'threshold', label: '超賣閾值', type: 'number', default: 30 },
  ],
  RSI_OVERBOUGHT: [
    { key: 'period', label: 'RSI 週期', type: 'number', default: 14 },
    { key: 'threshold', label: '超買閾值', type: 'number', default: 70 },
  ],
  MACD_CROSS_UP: [
    { key: 'fast', label: '快線週期', type: 'number', default: 12 },
    { key: 'slow', label: '慢線週期', type: 'number', default: 26 },
    { key: 'signal', label: '訊號線週期', type: 'number', default: 9 },
  ],
  KD_CROSS_UP: [
    { key: 'period', label: 'RSV 週期', type: 'number', default: 9 },
    { key: 'k_smooth', label: 'K 平滑', type: 'number', default: 3 },
    { key: 'd_smooth', label: 'D 平滑', type: 'number', default: 3 },
  ],
  BOLLINGER_BREAKOUT: [
    { key: 'period', label: '週期', type: 'number', default: 20 },
    { key: 'std_dev', label: '標準差倍數', type: 'number', default: 2 },
  ],
  PRICE_BREAKOUT_HIGH: [
    { key: 'period', label: '回顧週期', type: 'number', default: 20 },
  ],
};

const StrategySettings: React.FC<StrategySettingsProps> = ({ settings, onChange }) => {

  const handleStrategyChange = (type: 'entry' | 'exit', strategyName: string) => {
    // 取得該策略的預設參數
    const defs = STRATEGY_PARAM_DEFINITIONS[strategyName] || [];
    const newParams: Record<string, StrategyParamValue> = {};
    defs.forEach(d => {
      newParams[d.key] = d.default;
    });

    if (type === 'entry') {
      onChange({ entry_strategy: strategyName, entry_params: newParams });
    } else {
      onChange({ exit_strategy: strategyName, exit_params: newParams });
    }
  };

  const handleParamChange = (type: 'entry' | 'exit', key: string, value: number) => {
    if (type === 'entry') {
      onChange({ entry_params: { ...settings.entry_params, [key]: value } });
    } else {
      onChange({ exit_params: { ...settings.exit_params, [key]: value } });
    }
  };

  const renderParams = (type: 'entry' | 'exit', strategyName: string, params: Record<string, StrategyParamValue>) => {
    const defs = STRATEGY_PARAM_DEFINITIONS[strategyName] || [];
    if (defs.length === 0) return null;

    return (
      <div className="grid grid-cols-2 gap-4 mt-3 bg-gray-50 p-3 rounded-lg border border-gray-100">
        {defs.map((def) => (
          <div key={def.key}>
            <label className="block text-xs font-medium text-gray-500 mb-1">
              {def.label}
            </label>
            <input
              type="number"
              value={params[def.key]}
              onChange={(e) => handleParamChange(type, def.key, Number(e.target.value))}
              className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-teal-500 focus:border-teal-500 outline-none"
            />
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <span className="text-xl">🎯</span>
        策略設定
      </h3>

      <div className="space-y-6">
        {/* 進場策略 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            進場策略
          </label>
          <select
            value={settings.entry_strategy}
            onChange={(e) => handleStrategyChange('entry', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none bg-white"
          >
            {STRATEGY_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
          {renderParams('entry', settings.entry_strategy, settings.entry_params)}
        </div>

        {/* 分隔線 */}
        <div className="border-t border-gray-100"></div>

        {/* 出場策略 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            出場策略
          </label>
          <select
            value={settings.exit_strategy}
            onChange={(e) => handleStrategyChange('exit', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none bg-white"
          >
            <option value="SAME_AS_ENTRY">與進場策略相同 (反向)</option>
            {STRATEGY_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
          {settings.exit_strategy !== 'SAME_AS_ENTRY' &&
            renderParams('exit', settings.exit_strategy, settings.exit_params)
          }
        </div>
      </div>
    </div>
  );
};

export default StrategySettings;
