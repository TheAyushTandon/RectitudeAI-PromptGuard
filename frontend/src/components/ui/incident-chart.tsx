import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';

interface IncidentChartProps {
  data: { label: string; value: number }[];
}

export const IncidentChart: React.FC<IncidentChartProps> = ({ data }) => {
  return (
    <div className="w-full h-full flex items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
          <XAxis 
            dataKey="label" 
            stroke="#ffffff20" 
            fontSize={11} 
            tickLine={false} 
            axisLine={false}
          />
          <YAxis 
            stroke="#ffffff20" 
            fontSize={11} 
            tickLine={false} 
            axisLine={false}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: "rgba(20, 20, 20, 0.9)", 
              border: "1px solid rgba(255, 255, 255, 0.1)",
              borderRadius: "12px",
              backdropFilter: "blur(10px)"
            }}
          />
          <Bar dataKey="value" fill="#FFFFFF" radius={[4, 4, 0, 0]} opacity={0.6} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default IncidentChart;
