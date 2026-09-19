import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend
} from 'recharts';
import { Loader2, TrendingUp, Search, AlertCircle, CheckCircle2 } from 'lucide-react';

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('7d'); // '7d', '30d', '6m'
  const [revenueData, setRevenueData] = useState([]);
  const [loadingRevenue, setLoadingRevenue] = useState(false);

  // Product Search & Forecast
  const [products, setProducts] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [forecastData, setForecastData] = useState(null);
  const [loadingForecast, setLoadingForecast] = useState(false);
  const [forecastError, setForecastError] = useState(null);

  useEffect(() => {
    fetchRevenueData();
  }, [timeRange]);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchRevenueData = async () => {
    setLoadingRevenue(true);
    try {
      const end = new Date();
      const start = new Date();
      let interval = 'D';

      if (timeRange === '7d') {
        start.setDate(end.getDate() - 7);
      } else if (timeRange === '30d') {
        start.setDate(end.getDate() - 30);
      } else if (timeRange === '6m') {
        start.setMonth(end.getMonth() - 6);
        interval = 'M';
      }

      const res = await api.get(`/analytics/revenue`, {
        params: {
          start_date: start.toISOString(),
          end_date: end.toISOString(),
          interval: interval
        }
      });
      if (res.data && res.data.data) {
        setRevenueData(res.data.data);
      }
    } catch (error) {
      console.error("Failed to fetch revenue", error);
    } finally {
      setLoadingRevenue(false);
    }
  };

  const fetchProducts = async () => {
    try {
      const res = await api.get(`/analytics/all-products`);
      if (res.data && res.data.data) {
        setProducts(res.data.data);
      }
    } catch (error) {
      console.error("Failed to fetch products", error);
    }
  };

  const handleProductSelect = async (e) => {
    const pid = e.target.value;
    setSelectedProductId(pid);
    if (!pid) {
      setForecastData(null);
      return;
    }
    
    setLoadingForecast(true);
    setForecastError(null);
    try {
      const res = await api.get(`/ml/forecast`, {
        params: {
          product_id: pid,
          days: 7
        }
      });
      if (res.data && res.data.forecast) {
        setForecastData(res.data.forecast);
      }
    } catch (error) {
      console.error("Failed to fetch forecast", error);
      setForecastError(error.response?.data?.detail || "Failed to load forecast");
      setForecastData(null);
    } finally {
      setLoadingForecast(false);
    }
  };

  const getPrescriptiveBadge = (data) => {
    if (!data || data.length < 6) return null;
    
    const firstThree = data.slice(0, 3).reduce((sum, item) => sum + item.predicted_demand, 0) / 3;
    const lastThree = data.slice(-3).reduce((sum, item) => sum + item.predicted_demand, 0) / 3;
    
    const isTrendingUp = lastThree > firstThree;
    
    if (isTrendingUp) {
      return (
        <div className="flex items-center gap-2 px-3 py-1.5 bg-yellow-100 text-yellow-800 rounded-full text-sm font-semibold border border-yellow-200">
          <AlertCircle size={16} /> Restock Recommended (Trending Up)
        </div>
      );
    } else {
      return (
        <div className="flex items-center gap-2 px-3 py-1.5 bg-green-100 text-green-800 rounded-full text-sm font-semibold border border-green-200">
          <CheckCircle2 size={16} /> Stock Adequate (Stable/Down)
        </div>
      );
    }
  };

  const formatCurrency = (value) => `₹${value.toLocaleString()}`;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-text-main flex items-center gap-3">
            <TrendingUp className="text-accent" size={32} />
            Advanced Analytics
          </h1>
          <p className="text-sidebar/60 mt-1">Deep-dive into historical performance and predictive ML forecasts.</p>
        </div>
      </div>

      {/* Historical Revenue Chart */}
      <div className="bg-card rounded-xl shadow-md border border-slate-200 overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-200 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white">
          <h2 className="text-lg font-bold text-text-main">Historical Revenue & Profit</h2>
          <div className="flex bg-slate-100 p-1 rounded-lg">
            {[
              { id: '7d', label: 'Last 7 Days' },
              { id: '30d', label: 'Last 30 Days' },
              { id: '6m', label: 'Last 6 Months' }
            ].map(f => (
              <button
                key={f.id}
                onClick={() => setTimeRange(f.id)}
                className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  timeRange === f.id 
                    ? 'bg-white text-sidebar shadow-sm border border-slate-200' 
                    : 'text-text-main/60 hover:text-sidebar'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>
        
        <div className="p-6 relative min-h-[350px]">
          {loadingRevenue ? (
            <div className="absolute inset-0 bg-white/60 backdrop-blur-sm z-10 flex items-center justify-center">
              <Loader2 className="animate-spin text-accent w-10 h-10" />
            </div>
          ) : revenueData.length > 0 ? (
            <div className="h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={revenueData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#222831" stopOpacity={0.1}/>
                      <stop offset="95%" stopColor="#222831" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#FFD369" stopOpacity={0.2}/>
                      <stop offset="95%" stopColor="#FFD369" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="timestamp" axisLine={false} tickLine={false} tick={{fill: '#64748B', fontSize: 12}} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748B', fontSize: 12}} tickFormatter={(val) => `₹${val/1000}k`} />
                  <Tooltip 
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    formatter={(value) => formatCurrency(value)}
                  />
                  <Legend verticalAlign="top" height={36} />
                  <Area type="monotone" name="Revenue" dataKey="total_price" stroke="#222831" strokeWidth={3} fillOpacity={1} fill="url(#colorRevenue)" />
                  <Area type="monotone" name="Profit" dataKey="profit" stroke="#FFD369" strokeWidth={3} fillOpacity={1} fill="url(#colorProfit)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-500">
              No revenue data found for this period.
            </div>
          )}
        </div>
      </div>

      {/* AI Product Forecast Section */}
      <div className="bg-card rounded-xl shadow-md border border-slate-200 overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-200 bg-sidebar">
          <h2 className="text-lg font-bold text-canvas flex items-center gap-2">
            <Search className="text-accent" size={20} />
            Product Demand Forecast (AI)
          </h2>
        </div>
        
        <div className="p-6">
          <div className="max-w-md mb-8">
            <label className="block text-sm font-medium text-sidebar mb-2">Select a product to view its 7-day AI demand forecast</label>
            <select 
              className="w-full rounded-lg border border-slate-300 px-4 py-3 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-slate-50 font-medium"
              value={selectedProductId}
              onChange={handleProductSelect}
            >
              <option value="">-- Choose a Product --</option>
              {products.map(p => (
                <option key={p.id} value={p.id}>
                  [{p.product_code || 'N/A'}] {p.name} (Stock: {p.current_stock})
                </option>
              ))}
            </select>
          </div>

          <div className="relative min-h-[300px] border border-slate-100 rounded-xl p-4 bg-slate-50">
            {loadingForecast && (
              <div className="absolute inset-0 bg-white/60 backdrop-blur-sm z-10 flex items-center justify-center rounded-xl">
                <Loader2 className="animate-spin text-accent w-10 h-10" />
              </div>
            )}
            
            {!selectedProductId && !loadingForecast && (
              <div className="flex flex-col items-center justify-center h-full py-16 text-slate-400">
                <Search size={48} className="mb-4 opacity-20" />
                <p>Select a product above to generate a forecast.</p>
              </div>
            )}

            {forecastError && (
              <div className="flex flex-col items-center justify-center h-full py-16 text-red-500">
                <AlertCircle size={48} className="mb-4 opacity-50" />
                <p>{forecastError}</p>
              </div>
            )}

            {forecastData && !loadingForecast && !forecastError && (
              <div className="space-y-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-bold text-sidebar">7-Day Predicted Demand</h3>
                    <p className="text-sidebar/60 text-sm mt-1">XGBoost machine learning model prediction based on historical trends.</p>
                  </div>
                  {getPrescriptiveBadge(forecastData)}
                </div>
                
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={forecastData} margin={{ top: 20, right: 0, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                      <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#64748B', fontSize: 12}} dy={10} />
                      <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748B', fontSize: 12}} />
                      <Tooltip 
                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        cursor={{fill: '#f8fafc'}}
                      />
                      <Bar 
                        name="Predicted Units to Sell" 
                        dataKey="predicted_demand" 
                        fill="#FFD369" 
                        radius={[4, 4, 0, 0]}
                        barSize={40}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
