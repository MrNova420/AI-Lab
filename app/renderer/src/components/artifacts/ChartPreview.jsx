/**
 * Chart Preview Component
 * Interactive chart visualization
 */

import React from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

const ChartPreview = ({ artifact }) => {
  // Parse chart data and config
  const parseChartConfig = () => {
    try {
      return JSON.parse(artifact.content);
    } catch {
      return { type: 'line', data: [], config: {} };
    }
  };
  
  const { type, data, config = {} } = parseChartConfig();
  
  const renderChart = () => {
    switch (type) {
      case 'line':
        return (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={config.xKey || 'name'} />
            <YAxis />
            <Tooltip />
            <Legend />
            {(config.lines || ['value']).map((lineKey, index) => (
              <Line
                key={lineKey}
                type="monotone"
                dataKey={lineKey}
                stroke={COLORS[index % COLORS.length]}
                strokeWidth={2}
              />
            ))}
          </LineChart>
        );
      
      case 'bar':
        return (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={config.xKey || 'name'} />
            <YAxis />
            <Tooltip />
            <Legend />
            {(config.bars || ['value']).map((barKey, index) => (
              <Bar
                key={barKey}
                dataKey={barKey}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </BarChart>
        );
      
      case 'pie':
        return (
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={(entry) => entry.name}
              outerRadius={80}
              fill="#8884d8"
              dataKey={config.valueKey || 'value'}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        );
      
      case 'area':
        return (
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={config.xKey || 'name'} />
            <YAxis />
            <Tooltip />
            <Legend />
            {(config.areas || ['value']).map((areaKey, index) => (
              <Area
                key={areaKey}
                type="monotone"
                dataKey={areaKey}
                stroke={COLORS[index % COLORS.length]}
                fill={COLORS[index % COLORS.length]}
                fillOpacity={0.6}
              />
            ))}
          </AreaChart>
        );
      
      default:
        return <div>Unknown chart type: {type}</div>;
    }
  };
  
  return (
    <div className="chart-preview">
      <ResponsiveContainer width="100%" height={400}>
        {renderChart()}
      </ResponsiveContainer>
      
      {config.title && (
        <div className="chart-title">{config.title}</div>
      )}
      
      {config.description && (
        <div className="chart-description">{config.description}</div>
      )}
    </div>
  );
};

export default ChartPreview;
