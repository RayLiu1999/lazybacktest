import React from 'react';
import type { TradingSettings as ITradingSettings } from '../../types/api';

interface TradingSettingsProps {
  settings: ITradingSettings;
  onChange: (updates: Partial<ITradingSettings>) => void;
}

const TradingSettings: React.FC<TradingSettingsProps> = ({ settings, onChange }) => {
  return (
    <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <span className="text-xl">💰</span>
        交易設定
      </h3>

      <div className="space-y-4">
        {/* 交易時機 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            交易時機
          </label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="timing"
                checked={settings.timing === 'N_CLOSE'}
                onChange={() => onChange({ timing: 'N_CLOSE' })}
                className="text-teal-500 focus:ring-teal-500"
              />
              <span className="text-sm text-gray-600">N日收盤</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="timing"
                checked={settings.timing === 'N1_OPEN'}
                onChange={() => onChange({ timing: 'N1_OPEN' })}
                className="text-teal-500 focus:ring-teal-500"
              />
              <span className="text-sm text-gray-600">N+1日開盤</span>
            </label>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {/* 買入手續費 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              買入手續費 (%)
            </label>
            <input
              type="number"
              step="0.0001"
              value={settings.buy_fee}
              onChange={(e) => onChange({ buy_fee: Number(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-all"
            />
          </div>

          {/* 賣出手續費 + 稅 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              賣出手續費+稅 (%)
            </label>
            <input
              type="number"
              step="0.0001"
              value={settings.sell_fee}
              onChange={(e) => onChange({ sell_fee: Number(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-all"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingSettings;
