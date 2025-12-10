import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { dashboardAPI } from '../../services/api';
import DashboardCard from '../layout/DashboardCard';

const TopProtocols = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await dashboardAPI.getTopProtocols(8);
        setData(response.data.data);
      } catch (error) {
        console.error('Error fetching top protocols:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const formatVolume = (value) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(1)}K`;
    return `$${value.toFixed(0)}`;
  };

  if (loading) {
    return (
      <DashboardCard title="Top Protocols">
        <div className="h-64 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      </DashboardCard>
    );
  }

  return (
    <DashboardCard title="Top Protocols by Volume">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical" margin={{ left: 80 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis type="number" stroke="#6b7280" tickFormatter={formatVolume} />
          <YAxis 
            dataKey="name" 
            type="category" 
            stroke="#6b7280"
            tick={{ fontSize: 12 }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1f2937', 
              border: 'none', 
              borderRadius: '8px',
              color: '#fff' 
            }}
            formatter={(value) => [formatVolume(value), 'Volume']}
          />
          <Bar 
            dataKey="volume" 
            fill="#8b5cf6" 
            radius={[0, 4, 4, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </DashboardCard>
  );
};

export default TopProtocols;
