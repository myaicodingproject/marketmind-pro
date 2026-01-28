import React from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import SectionChart from './SectionChart';

const MarketCharts = ({ data }) => {
  const formatPercent = (value) => `${value}%`;

  return (
    <div className="market-charts">
      <SectionChart title="Stock Price Performance" height={350}>
        <AreaChart data={data.priceHistory}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip formatter={(value) => [`$${value}`, 'Price']} />
          <Area type="monotone" dataKey="price" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
        </AreaChart>
      </SectionChart>

      <SectionChart title="Market Share Analysis" height={350}>
        <BarChart data={data.marketShare}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="company" />
          <YAxis tickFormatter={formatPercent} />
          <Tooltip formatter={(value) => [`${value}%`, 'Market Share']} />
          <Bar dataKey="share" fill="#10b981" />
        </BarChart>
      </SectionChart>

      <SectionChart title="Industry Growth Trends" height={350}>
        <LineChart data={data.industryTrends}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis tickFormatter={formatPercent} />
          <Tooltip formatter={(value) => [`${value}%`, 'Growth Rate']} />
          <Legend />
          <Line type="monotone" dataKey="industry" stroke="#3b82f6" strokeWidth={2} name="Industry" />
          <Line type="monotone" dataKey="company" stroke="#10b981" strokeWidth={2} name="Company" />
        </LineChart>
      </SectionChart>

      <SectionChart title="Trading Volume" height={300}>
        <BarChart data={data.volume}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip formatter={(value) => [`${(value / 1000000).toFixed(1)}M`, 'Volume']} />
          <Bar dataKey="volume" fill="#8b5cf6" />
        </BarChart>
      </SectionChart>
    </div>
  );
};

export default MarketCharts;