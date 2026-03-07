import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { EMOTION_COLORS, EMOTION_LABELS } from '../../utils/constants';
import t from '../../locales';

interface EmotionChartProps {
  distribution: Record<string, number>;
}

const EmotionChart: React.FC<EmotionChartProps> = ({ distribution }) => {
  const data = Object.entries(distribution).map(([key, value]) => ({
    name: EMOTION_LABELS[key] || key,
    value,
    color: EMOTION_COLORS[key] || '#999',
  }));

  if (data.length === 0) {
    return <div style={{ textAlign: 'center', color: '#999', padding: 40 }}>{t.report.noData}</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
          {data.map((entry, index) => (
            <Cell key={index} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default EmotionChart;
