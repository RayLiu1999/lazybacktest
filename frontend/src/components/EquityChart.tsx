import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface EquityChartProps {
  data: number[];
  initialCapital: number;
}

const EquityChart: React.FC<EquityChartProps> = ({ data, initialCapital }) => {
  const chartData = data.map((value, index) => ({
    day: index + 1,
    equity: value,
  }));

  const minEquity = Math.min(...data);
  const maxEquity = Math.max(...data);
  const padding = (maxEquity - minEquity) * 0.1 || 1000;

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-lg">
          <p className="text-gray-500 text-xs mb-1">交易日 #{label}</p>
          <p className="text-teal-600 font-bold">
            ${Number(payload[0].value).toLocaleString()}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-80 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
          <XAxis
            dataKey="day"
            stroke="#9ca3af"
            tick={{ fill: '#6b7280', fontSize: 11 }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            stroke="#9ca3af"
            tick={{ fill: '#6b7280', fontSize: 11 }}
            domain={[minEquity - padding, maxEquity + padding]}
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
            tickLine={false}
            axisLine={false}
            width={55}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={initialCapital} stroke="#ef4444" strokeDasharray="3 3" />
          <Line
            type="monotone"
            dataKey="equity"
            stroke="#0d9488"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#0d9488', stroke: '#fff', strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EquityChart;
