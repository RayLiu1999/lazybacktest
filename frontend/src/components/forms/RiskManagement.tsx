import React from 'react';
import type { RiskSettings } from '../../types/api';

interface RiskManagementProps {
  settings: RiskSettings;
  onChange: (updates: Partial<RiskSettings>) => void;
}

const RiskManagement: React.FC<RiskManagementProps> = ({ settings, onChange }) => {
  return (
    <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <span className="text-xl">🛡️</span>
        風險管理
      </h3>

      <div className="space-y-4">
        {/* 倉位基準 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            倉位基準
          </label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="position_basis"
                checked={settings.position_basis === 'INITIAL_CAPITAL'}
                onChange={() => onChange({ position_basis: 'INITIAL_CAPITAL' })}
                className="text-teal-500 focus:ring-teal-500"
              />
              <span className="text-sm text-gray-600">初始資金</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="position_basis"
                checked={settings.position_basis === 'TOTAL_CAPITAL'}
                onChange={() => onChange({ position_basis: 'TOTAL_CAPITAL' })}
                className="text-teal-500 focus:ring-teal-500"
              />
              <span className="text-sm text-gray-600">目前總資金</span>
            </label>
          </div>
        </div>

        {/* 單次投入比例 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            單次投入比例 (%)
          </label>
          <input
            type="number"
            min="1"
            max="100"
            value={settings.position_pct}
            onChange={(e) => onChange({ position_pct: Number(e.target.value) })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-all"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          {/* 固定停損 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              固定停損 (%)
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              placeholder="無"
              value={settings.stop_loss !== undefined ? settings.stop_loss * 100 : ''}
              onChange={(e) => onChange({ stop_loss: e.target.value ? Number(e.target.value) / 100 : undefined })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-all"
            />
          </div>

          {/* 固定停利 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              固定停利 (%)
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              placeholder="無"
              value={settings.take_profit !== undefined ? settings.take_profit * 100 : ''}
              onChange={(e) => onChange({ take_profit: e.target.value ? Number(e.target.value) / 100 : undefined })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-all"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskManagement;
