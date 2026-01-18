import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceDot,
} from 'recharts';
import type { Trade } from '../types/api';

interface EquityChartProps {
  data: { date: string; equity: number; return_pct: number; drawdown: number }[];
  buyHoldData?: { date: string; equity: number; return_pct: number }[];
  trades?: Trade[];
  initialCapital: number;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ value: number; name: string; color: string }>;
  label?: string;
}

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-lg">
        <p className="text-gray-500 text-xs mb-2">{label}</p>
        {payload.map((item, index) => (
          <p key={index} style={{ color: item.color }} className="font-medium text-sm">
            {item.name}: {item.value.toFixed(2)}%
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const EquityChart: React.FC<EquityChartProps> = ({ data, buyHoldData, trades }) => {
  // Combine strategy and buy&hold data for dual-line chart
  const chartData = data.map((item, index) => {
    const buyHold = buyHoldData?.[index];
    return {
      date: item.date,
      strategy: item.return_pct,
      buyHold: buyHold?.return_pct ?? null,
    };
  });

  // Find trade points for markers
  const buyPoints = trades?.filter(t => t.action === 'BUY').map(t => t.date) || [];
  const sellPoints = trades?.filter(t => t.action === 'SELL').map(t => t.date) || [];

  // Calculate Y-axis domain
  const allValues = chartData.flatMap(d => [d.strategy, d.buyHold]).filter(v => v !== null) as number[];
  const minValue = Math.min(...allValues, 0);
  const maxValue = Math.max(...allValues);
  const padding = (maxValue - minValue) * 0.1 || 10;

  // Format date for X-axis (show only every Nth label to avoid crowding)
  const formatXAxis = (date: string) => {
    return date; // Already in YYYY-MM-DD format
  };

  return (
    <div className="h-96 w-full">
      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mb-4 text-sm">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-gray-400"></span>
          <span className="text-gray-600">買入並持有 %</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-blue-500"></span>
          <span className="text-gray-600">策略 %</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-red-500 text-lg">▲</span>
          <span className="text-gray-600">買入</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-green-500 text-lg">▼</span>
          <span className="text-gray-600">賣出</span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
          <XAxis
            dataKey="date"
            stroke="#9ca3af"
            tick={{ fill: '#6b7280', fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            angle={-45}
            textAnchor="end"
            height={60}
            tickFormatter={formatXAxis}
            interval={Math.floor(chartData.length / 10)} // Show ~10 labels
          />
          <YAxis
            stroke="#9ca3af"
            tick={{ fill: '#6b7280', fontSize: 11 }}
            domain={[minValue - padding, maxValue + padding]}
            tickFormatter={(value) => `${value.toFixed(0)}%`}
            tickLine={false}
            axisLine={false}
            width={55}
            label={{ value: '收益率 (%)', angle: -90, position: 'insideLeft', style: { fontSize: 12, fill: '#6b7280' } }}
          />
          <Tooltip content={<CustomTooltip />} />

          {/* Buy & Hold Line (gray, background) */}
          {buyHoldData && (
            <Line
              type="monotone"
              dataKey="buyHold"
              stroke="#9ca3af"
              strokeWidth={1.5}
              dot={false}
              name="買入並持有 %"
            />
          )}

          {/* Strategy Line (blue, foreground) */}
          <Line
            type="monotone"
            dataKey="strategy"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#3b82f6', stroke: '#fff', strokeWidth: 2 }}
            name="策略 %"
          />

          {/* Buy markers */}
          {buyPoints.map((date, i) => {
            const point = chartData.find(d => d.date === date);
            if (!point) return null;
            return (
              <ReferenceDot
                key={`buy-${i}`}
                x={date}
                y={point.strategy}
                r={6}
                fill="#ef4444"
                stroke="#fff"
                strokeWidth={2}
              />
            );
          })}

          {/* Sell markers */}
          {sellPoints.map((date, i) => {
            const point = chartData.find(d => d.date === date);
            if (!point) return null;
            return (
              <ReferenceDot
                key={`sell-${i}`}
                x={date}
                y={point.strategy}
                r={6}
                fill="#22c55e"
                stroke="#fff"
                strokeWidth={2}
              />
            );
          })}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EquityChart;
