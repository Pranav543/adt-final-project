import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import Header from './layout/Header';
import Sidebar from './layout/Sidebar';
import DashboardCard from './layout/DashboardCard';
import ProtocolDistribution from './charts/ProtocolDistribution';
import BlockchainContracts from './charts/BlockchainContracts';
import TransactionVolume from './charts/TransactionVolume';
import TopProtocols from './charts/TopProtocols';
import UserActivity from './charts/UserActivity';
import MarketPerformance from './charts/MarketPerformance';
import GasFeeAnalysis from './charts/GasFeeAnalysis';
import ProtocolMarketShare from './charts/ProtocolMarketShare';
import { Layers, FileCode, Users, ArrowLeftRight, TrendingUp, Globe } from 'lucide-react';

const StatCard = ({ title, value, icon: Icon, color }) => (
  <div className="bg-white rounded-xl shadow-lg p-6 flex items-center space-x-4">
    <div className={`p-3 rounded-lg ${color}`}>
      <Icon className="h-6 w-6 text-white" />
    </div>
    <div>
      <p className="text-sm text-gray-500">{title}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  </div>
);

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await dashboardAPI.getSummary();
        setSummary(response.data.data);
      } catch (error) {
        console.error('Error fetching summary:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num?.toLocaleString() || '0';
  };

  const formatVolume = (num) => {
    if (num >= 1000000) return `$${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `$${(num / 1000).toFixed(1)}K`;
    return `$${num?.toFixed(0) || '0'}`;
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1">
        <Header />
        <main className="p-6">
          {/* Stats Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
            <StatCard 
              title="Total Protocols" 
              value={loading ? '...' : formatNumber(summary?.totalProtocols)}
              icon={Layers}
              color="bg-indigo-600"
            />
            <StatCard 
              title="Total Contracts" 
              value={loading ? '...' : formatNumber(summary?.totalContracts)}
              icon={FileCode}
              color="bg-purple-600"
            />
            <StatCard 
              title="Total Users" 
              value={loading ? '...' : formatNumber(summary?.totalUsers)}
              icon={Users}
              color="bg-pink-600"
            />
            <StatCard 
              title="Transactions" 
              value={loading ? '...' : formatNumber(summary?.totalTransactions)}
              icon={ArrowLeftRight}
              color="bg-amber-600"
            />
            <StatCard 
              title="Total Volume" 
              value={loading ? '...' : formatVolume(summary?.totalVolume)}
              icon={TrendingUp}
              color="bg-emerald-600"
            />
            <StatCard 
              title="Blockchains" 
              value={loading ? '...' : summary?.uniqueBlockchains}
              icon={Globe}
              color="bg-cyan-600"
            />
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <ProtocolDistribution />
            <BlockchainContracts />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <TransactionVolume />
            <TopProtocols />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <UserActivity />
            <MarketPerformance />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <GasFeeAnalysis />
            <ProtocolMarketShare />
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
