import React from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import SectionChart from './SectionChart';

const FinancialCharts = ({ data }) => {
  const formatCurrency = (value) => `$${(value / 1000000).toFixed(1)}M`;

  return (
    <div className="financial-charts">
      <SectionChart title="Revenue Growth" height={350}>
        <LineChart data={data.revenue}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis tickFormatter={formatCurrency} />
          <Tooltip formatter={(value) => [formatCurrency(value), 'Revenue']} />
          <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={3} />
        </LineChart>
      </SectionChart>

      <SectionChart title="Profitability Metrics" height={350}>
        <BarChart data={data.profitability}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis tickFormatter={formatCurrency} />
          <Tooltip formatter={(value) => [formatCurrency(value)]} />
          <Legend />
          <Bar dataKey="grossProfit" fill="#10b981" name="Gross Profit" />
          <Bar dataKey="netIncome" fill="#3b82f6" name="Net Income" />
        </BarChart>
      </SectionChart>

      <SectionChart title="Cash Flow Analysis" height={350}>
        <LineChart data={data.cashFlow}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis tickFormatter={formatCurrency} />
          <Tooltip formatter={(value) => [formatCurrency(value)]} />
          <Legend />
          <Line type="monotone" dataKey="operating" stroke="#059669" strokeWidth={2} name="Operating CF" />
          <Line type="monotone" dataKey="free" stroke="#dc2626" strokeWidth={2} name="Free CF" />
        </LineChart>
      </SectionChart>
    </div>
  );
};

export default FinancialCharts;