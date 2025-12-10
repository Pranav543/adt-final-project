import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { dashboardAPI } from '../../services/api';
import DashboardCard from '../layout/DashboardCard';

const TransactionVolume = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await dashboardAPI.getTransactionVolume(30);
        setData(response.data.data);
      } catch (error) {
        console.error('Error fetching transaction volume:', error);
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
      <DashboardCard title="Transaction Volume">
        <div className="h-64 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      </DashboardCard>
    );
  }

  return (
    <DashboardCard title="Transaction Volume (30 Days)">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="date" 
            stroke="#6b7280"
            tick={{ fontSize: 10 }}
            tickFormatter={(value) => value.slice(5)}
          />
          <YAxis 
            stroke="#6b7280"
            tickFormatter={formatVolume}
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
          <Line 
            type="monotone" 
            dataKey="volume" 
            stroke="#6366f1" 
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 6, fill: '#6366f1' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </DashboardCard>
  );
};

export default TransactionVolume;
