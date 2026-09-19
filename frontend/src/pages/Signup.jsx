import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { TrendingUp, Loader2, Mail } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../services/api';

const Signup = () => {
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    let interval;
    if (resendCooldown > 0) {
      interval = setInterval(() => {
        setResendCooldown((prev) => prev - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [resendCooldown]);

  const handleSignupSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await api.post('/auth/register', { name, email, password });
      toast.success('Account created! Please check your email for the OTP.');
      setStep(2);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create account. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifySubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await api.post('/auth/verify-email', { email, otp });
      toast.success('Email verified successfully! Please sign in.');
      navigate('/login');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Invalid OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    if (resendCooldown > 0) return;
    try {
      await api.post('/auth/resend-otp', { email });
      toast.success('A new OTP has been sent.');
      setResendCooldown(60);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to resend OTP.');
    }
  };

  return (
    <div className="min-h-screen bg-canvas flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-card rounded-2xl shadow-xl border border-slate-200 p-8 space-y-6">
        
        {step === 1 ? (
          <>
            <div className="flex flex-col items-center justify-center text-center space-y-2 mb-8">
              <div className="w-16 h-16 bg-sidebar rounded-full flex items-center justify-center mb-2">
                <TrendingUp className="text-accent" size={32} />
              </div>
              <h1 className="text-2xl font-bold text-text-main">Create Account</h1>
              <p className="text-text-main/70 text-sm">Join ShubhLabh360 today</p>
            </div>

            <form onSubmit={handleSignupSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-main mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent bg-slate-50 text-text-main transition-colors"
                  placeholder="John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>

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
                {loading ? <Loader2 className="animate-spin text-accent w-5 h-5" /> : 'Create Account'}
              </button>
            </form>

            <p className="mt-8 text-center text-sm text-slate-500">
              Already have an account?{' '}
              <Link to="/login" className="font-bold text-slate-900 hover:text-brand transition-colors">
                Sign in
              </Link>
            </p>
          </>
        ) : (
          <>
            <div className="flex flex-col items-center justify-center text-center space-y-2 mb-8">
              <div className="w-16 h-16 bg-sidebar rounded-full flex items-center justify-center mb-2">
                <Mail className="text-accent" size={32} />
              </div>
              <h1 className="text-2xl font-bold text-text-main">Verify Email</h1>
              <p className="text-text-main/70 text-sm">
                We've sent a 6-digit verification code to <br />
                <span className="font-bold">{email}</span>
              </p>
            </div>

            <form onSubmit={handleVerifySubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-main mb-1 text-center">Enter OTP</label>
                <input
                  type="text"
                  required
                  maxLength={6}
                  className="w-full text-center tracking-widest text-2xl px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent bg-slate-50 text-text-main transition-colors"
                  placeholder="------"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                />
              </div>

              <button
                type="submit"
                disabled={loading || otp.length !== 6}
                className="w-full bg-sidebar hover:bg-slate-800 text-white font-medium py-3 rounded-lg shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2 disabled:opacity-70 flex justify-center items-center"
              >
                {loading ? <Loader2 className="animate-spin text-accent w-5 h-5" /> : 'Verify Account'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <button
                type="button"
                onClick={handleResend}
                disabled={resendCooldown > 0}
                className="text-sm font-medium text-slate-500 hover:text-slate-800 disabled:opacity-50 transition-colors"
              >
                {resendCooldown > 0 
                  ? `Resend OTP in ${resendCooldown}s` 
                  : "Didn't receive code? Resend"}
              </button>
            </div>
          </>
        )}

      </div>
    </div>
  );
};

export default Signup;
