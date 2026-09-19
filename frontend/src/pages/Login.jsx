import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { TrendingUp, Loader2 } from 'lucide-react';
import { Link as RouterLink, useNavigate as routerUseNavigate } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = routerUseNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const success = await login(email, password);
      if (success) {
        toast.success("Login Successful!");
        navigate('/');
      } else {
        toast.error('Invalid credentials');
      }
    } catch (err) {
      toast.error('An error occurred during login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-canvas flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-card rounded-2xl shadow-xl border border-slate-200 p-8 space-y-6">
        <div className="flex flex-col items-center justify-center text-center space-y-2 mb-8">
          <div className="w-16 h-16 bg-sidebar rounded-full flex items-center justify-center mb-2">
            <TrendingUp className="text-accent" size={32} />
          </div>
          <h1 className="text-2xl font-bold text-text-main">Welcome Back</h1>
          <p className="text-text-main/70 text-sm">Sign in to your ShubhLabh Analytics account</p>
        </div>



        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-main mb-1">Email Address</label>
            <input
              type="email"
              required
              className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent bg-slate-50 text-text-main transition-colors"
              placeholder="admin@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-text-main mb-1">Password</label>
            <input
              type="password"
              required
              className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent bg-slate-50 text-text-main transition-colors"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-sidebar hover:bg-slate-800 text-white font-medium py-3 rounded-lg shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2 disabled:opacity-70 flex justify-center items-center"
          >
            {loading ? <Loader2 className="animate-spin text-accent w-5 h-5" /> : 'Sign In'}
          </button>
        </form>

        <p className="mt-8 text-center text-sm text-slate-500">
          Don't have an account?{' '}
          <RouterLink to="/signup" className="font-bold text-slate-900 hover:text-brand transition-colors">
            Sign up
          </RouterLink>
        </p>
      </div>
    </div>
  );
};

export default Login;
