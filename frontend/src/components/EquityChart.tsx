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
import './EquityChart.css';

interface EquityChartProps {
  data: number[];
  initialCapital: number;
}

const EquityChart: React.FC<EquityChartProps> = ({ data, initialCapital }) => {
  // 轉換數據格式
  const chartData = data.map((value, index) => ({
    day: index + 1,
    equity: value,
    returnPct: ((value - initialCapital) / initialCapital) * 100,
  }));

  const minEquity = Math.min(...data);
  const maxEquity = Math.max(...data);
  const padding = (maxEquity - minEquity) * 0.1;

  return (
    <div className="equity-chart">
      <h3>📈 權益曲線</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <defs>
            <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00d9ff" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#00d9ff" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis
            dataKey="day"
            stroke="#8b8b8b"
            tick={{ fill: '#8b8b8b' }}
            label={{ value: '交易日', position: 'insideBottomRight', offset: -5, fill: '#8b8b8b' }}
          />
          <YAxis
            stroke="#8b8b8b"
            tick={{ fill: '#8b8b8b' }}
            domain={[minEquity - padding, maxEquity + padding]}
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`}
          />
          <Tooltip
            contentStyle={{
              background: 'rgba(26, 26, 46, 0.95)',
              border: '1px solid rgba(0, 217, 255, 0.3)',
              borderRadius: '8px',
              color: '#fff',
            }}
            formatter={(value) => [
              `$${Number(value).toLocaleString()}`,
              '權益',
            ]}
            labelFormatter={(label) => `第 ${label} 天`}
          />
          <ReferenceLine
            y={initialCapital}
            stroke="#ff6b6b"
            strokeDasharray="5 5"
            label={{ value: '初始資金', fill: '#ff6b6b', fontSize: 12 }}
          />
          <Line
            type="monotone"
            dataKey="equity"
            stroke="#00d9ff"
            strokeWidth={2}
            dot={false}
            fill="url(#equityGradient)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EquityChart;
