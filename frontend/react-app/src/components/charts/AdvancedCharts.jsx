import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  RadialBarChart,
  RadialBar,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

// Heatmap Component for DCF Sensitivity Analysis
export const HeatmapChart = ({ data, title = "DCF Sensitivity Analysis" }) => {
  if (!data || !data.values) return null;

  const heatmapData = [];
  data.wacc.forEach((wacc, waccIndex) => {
    data.growth.forEach((growth, growthIndex) => {
      heatmapData.push({
        wacc,
        growth,
        value: data.values[waccIndex][growthIndex],
        x: growthIndex,
        y: waccIndex
      });
    });
  });

  const getColor = (value) => {
    const min = Math.min(...data.values.flat());
    const max = Math.max(...data.values.flat());
    const ratio = (value - min) / (max - min);
    const hue = (1 - ratio) * 120; // Green to red
    return `hsl(${hue}, 70%, 50%)`;
  };

  return (
    <div className="chart-container">
      <h3 className="text-lg font-semibold mb-3">{title}</h3>
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              type="number" 
              dataKey="x" 
              domain={[0, data.growth.length - 1]}
              ticks={[0, 1, 2]}
              tickFormatter={(value) => `${data.growth[Math.round(value)]}%`}
              name="Growth Rate"
            />
            <YAxis 
              type="number" 
              dataKey="y" 
              domain={[0, data.wacc.length - 1]}
              ticks={[0, 1, 2, 3, 4]}
              tickFormatter={(value) => `${data.wacc[Math.round(value)]}%`}
              name="WACC"
            />
            <Tooltip 
              formatter={(value, name, props) => [
                `$${props.payload.value}`,
                `WACC: ${data.wacc[props.payload.y]}%, Growth: ${data.growth[props.payload.x]}%`
              ]}
            />
            <Scatter data={heatmapData}>
              {heatmapData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(entry.value)} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// Waterfall Chart for Cash Flow Analysis
export const WaterfallChart = ({ data, title = "Cash Flow Waterfall" }) => {
  if (!data) return null;

  const waterfallData = data.map((item, index) => ({
    ...item,
    cumulative: data.slice(0, index + 1).reduce((sum, d) => sum + d.value, 0)
  }));

  return (
    <div className="chart-container">
      <h3 className="text-lg font-semibold mb-3">{title}</h3>
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={waterfallData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" />
            <YAxis />
            <Tooltip formatter={(value) => [`$${value}M`, 'Value']} />
            <Bar 
              dataKey="value" 
              fill={(entry) => entry.value >= 0 ? '#00C49F' : '#FF8042'}
            />
            <Line 
              type="monotone" 
              dataKey="cumulative" 
              stroke="#8884D8" 
              strokeWidth={2}
              dot={{ r: 4 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// Gauge Chart for Metrics
export const GaugeChart = ({ value, max = 100, title = "Score", color = "#0088FE" }) => {
  const data = [
    { name: 'Score', value, fill: color },
    { name: 'Remaining', value: max - value, fill: '#f0f0f0' }
  ];

  return (
    <div className="chart-container">
      <h3 className="text-lg font-semibold mb-3">{title}</h3>
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <ResponsiveContainer width="100%" height={200}>
          <RadialBarChart 
            cx="50%" 
            cy="50%" 
            innerRadius="60%" 
            outerRadius="90%" 
            data={data}
            startAngle={180}
            endAngle={0}
          >
            <RadialBar dataKey="value" cornerRadius={10} />
            <text 
              x="50%" 
              y="50%" 
              textAnchor="middle" 
              dominantBaseline="middle" 
              className="text-2xl font-bold"
            >
              {value}%
            </text>
          </RadialBarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// Area Chart with Confidence Bands
export const AreaChartWithBands = ({ data, title = "Revenue Projections" }) => {
  if (!data) return null;

  return (
    <div className="chart-container">
      <h3 className="text-lg font-semibold mb-3">{title}</h3>
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip formatter={(value) => [`$${value}B`, 'Revenue']} />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="high" 
              stackId="1" 
              stroke="#8884d8" 
              fill="#8884d8" 
              fillOpacity={0.2}
              name="High Estimate"
            />
            <Area 
              type="monotone" 
              dataKey="base" 
              stackId="2" 
              stroke="#82ca9d" 
              fill="#82ca9d" 
              fillOpacity={0.6}
              name="Base Case"
            />
            <Area 
              type="monotone" 
              dataKey="low" 
              stackId="3" 
              stroke="#ffc658" 
              fill="#ffc658" 
              fillOpacity={0.2}
              name="Low Estimate"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// Risk Matrix Scatter Plot
export const RiskMatrixChart = ({ data, title = "Risk Assessment Matrix" }) => {
  if (!data) return null;

  const getColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'high': return '#FF8042';
      case 'medium': return '#FFBB28';
      case 'low': return '#00C49F';
      default: return '#8884D8';
    }
  };

  return (
    <div className="chart-container">
      <h3 className="text-lg font-semibold mb-3">{title}</h3>
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              type="number" 
              dataKey="probability" 
              name="Probability" 
              unit="%" 
              domain={[0, 100]}
            />
            <YAxis 
              type="number" 
              dataKey="impact" 
              name="Impact" 
              domain={[0, 10]}
            />
            <Tooltip 
              cursor={{ strokeDasharray: '3 3' }}
              formatter={(value, name) => [value, name]}
              labelFormatter={(label, payload) => 
                payload?.[0]?.payload?.risk || 'Risk Factor'
              }
            />
            <Scatter data={data}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(entry.severity)} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};