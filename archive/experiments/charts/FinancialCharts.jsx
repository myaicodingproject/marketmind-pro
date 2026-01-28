import React from 'react';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, LineChart, Line, ResponsiveContainer
} from 'recharts';

// Corporate color palette
const COLORS = {
  primary: '#1f4e79',
  secondary: '#2e75b6',
  accent: '#4a90c2',
  light: '#7bb3d9',
  success: '#28a745',
  warning: '#ffc107',
  danger: '#dc3545'
};

const chartColors = [COLORS.primary, COLORS.secondary, COLORS.accent, COLORS.light, COLORS.success, COLORS.warning];

// Custom tooltip styling
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        backgroundColor: 'white',
        border: `2px solid ${COLORS.primary}`,
        borderRadius: '8px',
        padding: '12px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
      }}>
        <p style={{ color: COLORS.primary, fontWeight: 'bold', margin: 0 }}>
          {label}
        </p>
        {payload.map((entry, index) => (
          <p key={index} style={{ color: entry.color, margin: '4px 0' }}>
            {`${entry.name}: ${entry.value}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// 1. Revenue Breakdown Pie Chart
export const RevenueBreakdownChart = ({ data = sampleRevenueData, title = "Revenue Breakdown" }) => (
  <div style={{ width: '100%', height: '400px', padding: '20px' }}>
    <h3 style={{ color: COLORS.primary, textAlign: 'center', marginBottom: '20px' }}>{title}</h3>
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
          outerRadius={120}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  </div>
);

// 2. Financial Metrics Comparison Bar Chart
export const FinancialMetricsChart = ({ data = sampleMetricsData, title = "Financial Metrics Comparison" }) => (
  <div style={{ width: '100%', height: '400px', padding: '20px' }}>
    <h3 style={{ color: COLORS.primary, textAlign: 'center', marginBottom: '20px' }}>{title}</h3>
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="metric" tick={{ fill: COLORS.primary }} />
        <YAxis tick={{ fill: COLORS.primary }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Bar dataKey="current" fill={COLORS.primary} name="Current Year" />
        <Bar dataKey="previous" fill={COLORS.secondary} name="Previous Year" />
      </BarChart>
    </ResponsiveContainer>
  </div>
);

// 3. Valuation Analysis Chart
export const ValuationAnalysisChart = ({ data = sampleValuationData, title = "Valuation Analysis" }) => (
  <div style={{ width: '100%', height: '400px', padding: '20px' }}>
    <h3 style={{ color: COLORS.primary, textAlign: 'center', marginBottom: '20px' }}>{title}</h3>
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="period" tick={{ fill: COLORS.primary }} />
        <YAxis tick={{ fill: COLORS.primary }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Line type="monotone" dataKey="peRatio" stroke={COLORS.primary} strokeWidth={3} name="P/E Ratio" />
        <Line type="monotone" dataKey="pbRatio" stroke={COLORS.secondary} strokeWidth={3} name="P/B Ratio" />
        <Line type="monotone" dataKey="psRatio" stroke={COLORS.accent} strokeWidth={3} name="P/S Ratio" />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

// 4. Market Share Donut Chart
export const MarketShareChart = ({ data = sampleMarketShareData, title = "Market Share Analysis" }) => (
  <div style={{ width: '100%', height: '400px', padding: '20px' }}>
    <h3 style={{ color: COLORS.primary, textAlign: 'center', marginBottom: '20px' }}>{title}</h3>
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
          outerRadius={120}
          innerRadius={60}
          fill="#8884d8"
          dataKey="share"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  </div>
);

// Sample Data
export const sampleRevenueData = [
  { name: 'Product Sales', value: 45.2, amount: '$452M' },
  { name: 'Services', value: 28.7, amount: '$287M' },
  { name: 'Subscriptions', value: 18.3, amount: '$183M' },
  { name: 'Licensing', value: 7.8, amount: '$78M' }
];

export const sampleMetricsData = [
  { metric: 'Revenue', current: 1250, previous: 1180 },
  { metric: 'EBITDA', current: 320, previous: 285 },
  { metric: 'Net Income', current: 180, previous: 165 },
  { metric: 'Cash Flow', current: 220, previous: 195 }
];

export const sampleValuationData = [
  { period: 'Q1 2023', peRatio: 18.5, pbRatio: 2.8, psRatio: 4.2 },
  { period: 'Q2 2023', peRatio: 19.2, pbRatio: 3.1, psRatio: 4.5 },
  { period: 'Q3 2023', peRatio: 17.8, pbRatio: 2.9, psRatio: 4.1 },
  { period: 'Q4 2023', peRatio: 20.1, pbRatio: 3.3, psRatio: 4.8 },
  { period: 'Q1 2024', peRatio: 21.5, pbRatio: 3.5, psRatio: 5.1 }
];

export const sampleMarketShareData = [
  { name: 'Company A', share: 32.5 },
  { name: 'Company B', share: 24.8 },
  { name: 'Company C', share: 18.2 },
  { name: 'Company D', share: 12.7 },
  { name: 'Others', share: 11.8 }
];