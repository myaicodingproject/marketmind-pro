import React from 'react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import SectionChart from './SectionChart';

const RiskCharts = ({ data }) => {
  const riskColors = {
    'High': '#ef4444',
    'Medium': '#f59e0b', 
    'Low': '#10b981'
  };

  return (
    <div className="risk-charts">
      <SectionChart title="Risk Assessment by Category" height={350}>
        <BarChart data={data.categories}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="category" />
          <YAxis domain={[0, 10]} />
          <Tooltip formatter={(value) => [`${value}/10`, 'Risk Score']} />
          <Bar dataKey="score" fill={(entry) => riskColors[entry.level] || '#6b7280'} />
        </BarChart>
      </SectionChart>

      <SectionChart title="Risk Distribution" height={300}>
        <PieChart>
          <Pie
            data={data.distribution}
            cx="50%"
            cy="50%"
            outerRadius={80}
            dataKey="count"
            label={({ name, count }) => `${name}: ${count}`}
          >
            {data.distribution.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={riskColors[entry.name]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </SectionChart>

      <SectionChart title="Risk Impact vs Probability" height={350}>
        <BarChart data={data.matrix} layout="horizontal">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" domain={[0, 100]} />
          <YAxis dataKey="risk" type="category" width={120} />
          <Tooltip formatter={(value) => [`${value}%`, 'Impact Score']} />
          <Bar dataKey="impact" fill="#ef4444" />
        </BarChart>
      </SectionChart>
    </div>
  );
};

export default RiskCharts;