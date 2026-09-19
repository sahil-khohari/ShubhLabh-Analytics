import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const SalesChart = ({ data, loading }) => {
  return (
    <div className="w-full bg-card p-6 rounded-xl shadow-md border border-slate-200 relative">
      <h2 className="text-lg font-semibold text-text-main mb-6">Revenue vs Profit Trend</h2>
      
      {loading ? (
        <div className="absolute inset-0 z-10 bg-white/50 backdrop-blur-sm flex items-center justify-center rounded-xl">
          <div className="w-8 h-8 border-4 border-slate-200 border-t-accent rounded-full animate-spin"></div>
        </div>
      ) : null}

      {/* Chart */}
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#222831" stopOpacity={0.1}/>
                <stop offset="95%" stopColor="#222831" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorProf" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#FFD369" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#FFD369" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis dataKey="date" tick={{fontSize: 12, fill: '#64748b'}} axisLine={false} tickLine={false} />
            <YAxis tick={{fontSize: 12, fill: '#64748b'}} axisLine={false} tickLine={false} tickFormatter={(val) => `₹${val/1000}k`} />
            <Tooltip 
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', color: '#393E46' }}
              itemStyle={{ fontWeight: 500 }}
            />
            <Area type="monotone" dataKey="revenue" stroke="#222831" strokeWidth={3} fillOpacity={1} fill="url(#colorRev)" />
            <Area type="monotone" dataKey="profit" stroke="#FFD369" strokeWidth={3} fillOpacity={1} fill="url(#colorProf)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default SalesChart;
