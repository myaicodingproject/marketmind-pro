import React from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Area,
  AreaChart
} from 'recharts';
import { InteractiveChart } from './InteractiveFeatures';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

// Financial Analysis Charts
export const FinancialCharts = ({ data, onDataPointClick }) => {
  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Revenue Trend Chart */}
      {data.revenue_trend && (
        <InteractiveChart
          title="Revenue & Growth Trend"
          data={data.revenue_trend}
          filename="revenue-trend"
          series={['revenue', 'growth']}
          onDataPointClick={onDataPointClick}
        >
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={data.revenue_trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip formatter={(value, name) => [
                name === 'revenue' ? `$${value}B` : `${value}%`,
                name === 'revenue' ? 'Revenue' : 'Growth Rate'
              ]} />
              <Legend />
              <Bar yAxisId="left" dataKey="revenue" fill="#8884d8" name="Revenue ($B)" />
              <Line yAxisId="right" type="monotone" dataKey="growth" stroke="#82ca9d" strokeWidth={2} name="Growth (%)" />
            </ComposedChart>
          </ResponsiveContainer>
        </InteractiveChart>
      )}

      {/* Margins Chart */}
      {data.margins && (
        <InteractiveChart
          title="Profit Margins Analysis"
          data={data.margins}
          filename="profit-margins"
          onDataPointClick={onDataPointClick}
        >
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.margins}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="metric" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value}%`, 'Margin']} />
              <Bar dataKey="value" fill="#8884d8">
                {data.margins.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </InteractiveChart>
      )}

      {/* Segment Breakdown Pie Chart */}
      {data.segment_breakdown && (
        <InteractiveChart
          title="Revenue by Segment"
          data={data.segment_breakdown}
          filename="segment-breakdown"
          onDataPointClick={onDataPointClick}
        >
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data.segment_breakdown}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ segment, percentage }) => `${segment}: ${percentage}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="revenue"
              >
                {data.segment_breakdown.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`$${value}B`, 'Revenue']} />
            </PieChart>
          </ResponsiveContainer>
        </InteractiveChart>
      )}
    </div>
  );
};

// Valuation Analysis Charts
export const ValuationCharts = ({ data, onDataPointClick }) => {
  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Peer Comparison Chart */}
      {data.peer_comparison && (
        <InteractiveChart
          title="Peer Valuation Comparison"
          data={data.peer_comparison}
          filename="peer-comparison"
          series={['pe', 'ev_ebitda', 'price_sales']}
          onDataPointClick={onDataPointClick}
        >
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.peer_comparison}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="company" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="pe" fill="#8884d8" name="P/E Ratio" />
              <Bar dataKey="ev_ebitda" fill="#82ca9d" name="EV/EBITDA" />
              <Bar dataKey="price_sales" fill="#ffc658" name="Price/Sales" />
            </BarChart>
          </ResponsiveContainer>
        </InteractiveChart>
      )}

      {/* Price Target Breakdown */}
      {data.price_target_breakdown && (
        <InteractiveChart
          title="Price Target Methodology"
          data={data.price_target_breakdown}
          filename="price-target-breakdown"
          onDataPointClick={onDataPointClick}
        >
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={data.price_target_breakdown}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="method" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Bar yAxisId="left" dataKey="value" fill="#8884d8" name="Price Target ($)" />
              <Line yAxisId="right" type="monotone" dataKey="weight" stroke="#82ca9d" strokeWidth={2} name="Weight (%)" />
            </ComposedChart>
          </ResponsiveContainer>
        </InteractiveChart>
      )}
    </div>
  );
};

// Risk Assessment Charts
export const RiskCharts = ({ data, onDataPointClick }) => {
  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Scenario Analysis Chart */}
      {data.scenario_analysis && (
        <InteractiveChart
          title="Scenario Analysis"
          data={data.scenario_analysis}
          filename="scenario-analysis"
          onDataPointClick={onDataPointClick}
        >
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={data.scenario_analysis}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="scenario" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Bar yAxisId="left" dataKey="price_target" fill="#8884d8" name="Price Target ($)" />
              <Line yAxisId="right" type="monotone" dataKey="probability" stroke="#82ca9d" strokeWidth={2} name="Probability (%)" />
            </ComposedChart>
          </ResponsiveContainer>
        </InteractiveChart>
      )}
    </div>
  );
};

// Market Analysis Charts
export const MarketCharts = ({ data, onDataPointClick }) => {
  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Market Share Chart */}
      {data.market_share && (
        <InteractiveChart
          title="Geographic Market Share"
          data={data.market_share}
          filename="market-share"
          onDataPointClick={onDataPointClick}
        >
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={data.market_share}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="region" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Bar yAxisId="left" dataKey="share" fill="#8884d8" name="Market Share (%)" />
              <Line yAxisId="right" type="monotone" dataKey="growth" stroke="#82ca9d" strokeWidth={2} name="Growth (%)" />
            </ComposedChart>
          </ResponsiveContainer>
        </InteractiveChart>
      )}

      {/* Competitive Position Chart */}
      {data.competitive_position && (
        <InteractiveChart
          title="Competitive Position"
          data={data.competitive_position}
          filename="competitive-position"
          onDataPointClick={onDataPointClick}
        >
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data.competitive_position}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="competitor" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value}%`, 'Market Share']} />
              <Area type="monotone" dataKey="market_share" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
            </AreaChart>
          </ResponsiveContainer>
        </InteractiveChart>
      )}
    </div>
  );
};