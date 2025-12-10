import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { dashboardAPI } from '../../services/api';
import DashboardCard from '../layout/DashboardCard';

const GasFeeAnalysis = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await dashboardAPI.getGasAnalysis(30);
        setData(response.data.data);
      } catch (error) {
        console.error('Error fetching gas analysis:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <DashboardCard title="Gas Fee Analysis">
        <div className="h-64 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      </DashboardCard>
    );
  }

  return (
    <DashboardCard title="Gas Fee Analysis">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="date" 
            stroke="#6b7280"
            tick={{ fontSize: 10 }}
            tickFormatter={(value) => value.slice(5)}
          />
          <YAxis stroke="#6b7280" />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1f2937', 
              border: 'none', 
              borderRadius: '8px',
              color: '#fff' 
            }}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="avgGasPrice" 
            stroke="#6366f1" 
            strokeWidth={2}
            dot={false}
            name="Avg Gas Price (Gwei)"
          />
          <Line 
            type="monotone" 
            dataKey="avgFee" 
            stroke="#f59e0b" 
            strokeWidth={2}
            dot={false}
            name="Avg Fee ($)"
          />
        </LineChart>
      </ResponsiveContainer>
    </DashboardCard>
  );
};

export default GasFeeAnalysis;
