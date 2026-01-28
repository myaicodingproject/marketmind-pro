import React from 'react';
import { BarChart, Bar, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell } from 'recharts';
import SectionChart from './SectionChart';

const ValuationCharts = ({ data }) => {
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="valuation-charts">
      <SectionChart title="DCF Sensitivity Analysis" height={350}>
        <BarChart data={data.dcf}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="scenario" />
          <YAxis />
          <Tooltip formatter={(value) => [`$${value}`, 'Price Target']} />
          <Bar dataKey="priceTarget" fill="#3b82f6" />
        </BarChart>
      </SectionChart>

      <SectionChart title="Peer Comparison - P/E vs Growth" height={350}>
        <ScatterChart data={data.peers}>
          <CartesianGrid />
          <XAxis dataKey="peRatio" name="P/E Ratio" />
          <YAxis dataKey="growthRate" name="Growth Rate %" />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} 
                   formatter={(value, name) => [
                     name === 'peRatio' ? value.toFixed(1) : `${value}%`,
                     name === 'peRatio' ? 'P/E Ratio' : 'Growth Rate'
                   ]} />
          <Scatter dataKey="peRatio" fill="#3b82f6" />
        </ScatterChart>
      </SectionChart>

      <SectionChart title="Valuation Methods" height={300}>
        <PieChart>
          <Pie
            data={data.methods}
            cx="50%"
            cy="50%"
            outerRadius={80}
            dataKey="value"
            label={({ name, value }) => `${name}: $${value}`}
          >
            {data.methods.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </SectionChart>
    </div>
  );
};

export default ValuationCharts;