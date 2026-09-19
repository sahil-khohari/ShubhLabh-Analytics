import React, { useState, useEffect } from 'react';
import api from '../services/api';
import SalesChart from '../components/SalesChart';
import { IndianRupee, Percent, AlertCircle, Loader2 } from 'lucide-react';

const Dashboard = () => {
  const [revenueData, setRevenueData] = useState(null);
  const [productsData, setProductsData] = useState([]);
  const [anomaliesCount, setAnomaliesCount] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [revRes, prodRes, anomRes] = await Promise.all([
        api.get('/analytics/revenue?interval=M'),
        api.get('/analytics/products'),
        api.get('/ml/anomalies')
      ]);
      
      setRevenueData(revRes.data);
      setProductsData(prodRes.data.data.top_profitable.slice(0, 5));
      setAnomaliesCount(anomRes.data.anomalies_found || 0);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const chartData = revenueData?.data?.map(item => ({
    date: item.timestamp.substring(0, 7),
    revenue: item.total_price,
    profit: item.profit
  })) || [];

  const totalRev = revenueData?.data?.reduce((sum, item) => sum + item.total_price, 0) || 0;
  const totalProfit = revenueData?.data?.reduce((sum, item) => sum + item.profit, 0) || 0;
  const marginPct = totalRev > 0 ? (totalProfit / totalRev) * 100 : 0;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6 relative">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-text-main">Executive Overview</h1>
      </div>
      
      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-card p-6 rounded-xl shadow-md border border-slate-200 flex items-center gap-4">
          <div className="p-3 bg-slate-100 text-sidebar rounded-lg">
            <IndianRupee size={24} />
          </div>
          <div>
            <p className="text-sm text-text-main/70 font-medium">Total Revenue</p>
            {loading ? <div className="h-8 w-24 bg-slate-200 animate-pulse rounded mt-1"></div> : (
              <p className="text-2xl font-bold text-text-main">₹{totalRev.toLocaleString()}</p>
            )}
          </div>
        </div>
        
        <div className="bg-card p-6 rounded-xl shadow-md border border-slate-200 flex items-center gap-4">
          <div className="p-3 bg-accent/20 text-sidebar rounded-lg">
            <Percent size={24} />
          </div>
          <div>
            <p className="text-sm text-text-main/70 font-medium">Net Profit Margin</p>
            {loading ? <div className="h-8 w-20 bg-slate-200 animate-pulse rounded mt-1"></div> : (
              <p className="text-2xl font-bold text-text-main">{marginPct.toFixed(2)}%</p>
            )}
          </div>
        </div>

        <div className="bg-card p-6 rounded-xl shadow-md border border-slate-200 flex items-center gap-4">
          <div className="p-3 bg-red-50 text-anomaly rounded-lg">
            <AlertCircle size={24} />
          </div>
          <div>
            <p className="text-sm text-text-main/70 font-medium">Active Anomalies</p>
            {loading ? <div className="h-8 w-12 bg-slate-200 animate-pulse rounded mt-1"></div> : (
              <p className="text-2xl font-bold text-text-main">{anomaliesCount}</p>
            )}
          </div>
        </div>
      </div>

      {/* Chart */}
      <SalesChart data={chartData} loading={loading} />

      {/* Top Products Table */}
      <div className="bg-card rounded-xl shadow-md border border-slate-200 overflow-hidden relative">
        <div className="px-6 py-4 border-b border-slate-200">
          <h2 className="text-lg font-semibold text-text-main">Top 5 Profitable Products</h2>
        </div>
        {loading && <div className="absolute inset-0 top-14 bg-white/60 backdrop-blur-sm z-10 flex items-center justify-center"><Loader2 className="animate-spin text-accent w-8 h-8" /></div>}
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 text-text-main/70 text-sm">
              <th className="px-6 py-3 font-medium">Product ID</th>
              <th className="px-6 py-3 font-medium">Name</th>
              <th className="px-6 py-3 font-medium">Category</th>
              <th className="px-6 py-3 font-medium">Total Profit</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-text-main">
            {productsData.map((prod) => (
              <tr key={prod.product_id} className="hover:bg-slate-50">
                <td className="px-6 py-4">{prod.product_id}</td>
                <td className="px-6 py-4 font-medium">{prod.name}</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 bg-slate-100 text-text-main/80 rounded-full text-xs">
                    {prod.category}
                  </span>
                </td>
                <td className="px-6 py-4 text-accent font-bold">
                  ₹{prod.profit.toLocaleString()}
                </td>
              </tr>
            ))}
            {productsData.length === 0 && (
              <tr>
                <td colSpan="4" className="px-6 py-4 text-center text-text-main/50">
                  No product data available.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
};

export default Dashboard;
