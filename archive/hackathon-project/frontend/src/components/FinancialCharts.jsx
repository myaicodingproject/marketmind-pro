import React from 'react';
import {
  PieChart,
  Pie,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';

// Corporate colors
const COLORS = {
  primary: '#1f4e79',
  secondary: '#2e75b6',
  accent: '#4a90c2',
  light: '#7bb3d9',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444'
};

const CHART_COLORS = [COLORS.primary, COLORS.secondary, COLORS.accent, COLORS.light, COLORS.success, COLORS.warning];

// Sample data
export const sampleData = {
  revenue: [
    { name: 'Product Sales', value: 45, amount: 450000 },
    { name: 'Services', value: 30, amount: 300000 },
    { name: 'Licensing', value: 15, amount: 150000 },
    { name: 'Other', value: 10, amount: 100000 }
  ],
  metrics: [
    { metric: 'Revenue', current: 1000000, previous: 850000 },
    { metric: 'Profit', current: 250000, previous: 200000 },
    { metric: 'EBITDA', current: 350000, previous: 280000 },
    { metric: 'Cash Flow', current: 180000, previous: 150000 }
  ],
  valuation: [
    { period: 'Q1 2023', value: 12.5, benchmark: 11.8 },
    { period: 'Q2 2023', value: 13.2, benchmark: 12.1 },
    { period: 'Q3 2023', value: 14.1, benchmark: 12.5 },
    { period: 'Q4 2023', value: 15.3, benchmark: 13.2 }
  ],
  marketShare: [
    { name: 'Company', value: 35 },
    { name: 'Competitor A', value: 25 },
    { name: 'Competitor B', value: 20 },
    { name: 'Others', value: 20 }
  ]
};

// Custom tooltip styling
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
        {label && <p className="font-medium text-gray-900">{label}</p>}
        {payload.map((entry, index) => (
          <p key={index} style={{ color: entry.color }} className="text-sm">
            {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// 1. Revenue Breakdown Pie Chart
export const RevenueBreakdownChart = ({ data = sampleData.revenue, height = 300 }) => (
  <div className="bg-white p-4 rounded-lg border">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Breakdown</h3>
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          outerRadius={80}
          dataKey="value"
          label={({ name, value }) => `${name}: ${value}%`}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
      </PieChart>
    </ResponsiveContainer>
  </div>
);

// 2. Financial Metrics Comparison Bar Chart
export const MetricsComparisonChart = ({ data = sampleData.metrics, height = 300 }) => (
  <div className="bg-white p-4 rounded-lg border">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Financial Metrics Comparison</h3>
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="metric" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Bar dataKey="current" fill={COLORS.primary} name="Current Period" />
        <Bar dataKey="previous" fill={COLORS.secondary} name="Previous Period" />
      </BarChart>
    </ResponsiveContainer>
  </div>
);

// 3. Valuation Analysis Chart
export const ValuationAnalysisChart = ({ data = sampleData.valuation, height = 300 }) => (
  <div className="bg-white p-4 rounded-lg border">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Valuation Analysis</h3>
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="period" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="value" 
          stroke={COLORS.primary} 
          strokeWidth={3}
          name="Company Valuation"
          dot={{ fill: COLORS.primary, strokeWidth: 2, r: 4 }}
        />
        <Line 
          type="monotone" 
          dataKey="benchmark" 
          stroke={COLORS.secondary} 
          strokeWidth={2}
          strokeDasharray="5 5"
          name="Industry Benchmark"
          dot={{ fill: COLORS.secondary, strokeWidth: 2, r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

// 4. Market Share Donut Chart
export const MarketShareChart = ({ data = sampleData.marketShare, height = 300 }) => (
  <div className="bg-white p-4 rounded-lg border">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Share Analysis</h3>
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={40}
          outerRadius={80}
          dataKey="value"
          label={({ name, value }) => `${name}: ${value}%`}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
      </PieChart>
    </ResponsiveContainer>
  </div>
);

// Combined Dashboard Component
export const FinancialDashboard = ({ 
  revenueData, 
  metricsData, 
  valuationData, 
  marketShareData 
}) => (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
    <RevenueBreakdownChart data={revenueData} />
    <MetricsComparisonChart data={metricsData} />
    <ValuationAnalysisChart data={valuationData} />
    <MarketShareChart data={marketShareData} />
  </div>
);