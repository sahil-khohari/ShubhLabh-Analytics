import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Inventory from './pages/Inventory';
import Sales from './pages/Sales';
import Analytics from './pages/Analytics';
import AIAssistant from './pages/AIAssistant';
import Expenses from './pages/Expenses';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Profile from './pages/Profile';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AlertOctagon, X } from 'lucide-react';
import { Toaster } from 'react-hot-toast';

// A wrapper for protected routes
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="min-h-screen flex items-center justify-center bg-canvas">Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 ml-64 overflow-y-auto min-h-screen">
        {children}
      </main>
    </div>
  );
};

function AppContent() {
  useEffect(() => {
    // We handle auth-expired globally to reset context if needed
    const handleAuthExpired = () => {
      // It's handled gracefully in api.js now, but context could listen here if desired
    };
    window.addEventListener('auth-expired', handleAuthExpired);
    return () => window.removeEventListener('auth-expired', handleAuthExpired);
  }, []);

  return (
    <div className="bg-canvas min-h-screen font-sans text-slate-900 relative">
      <Toaster position="top-right" toastOptions={{
        className: 'font-sans',
        style: {
          background: '#FFFFFF',
          color: '#393E46',
          border: '1px solid #E2E8F0',
        },
        success: {
          iconTheme: {
            primary: '#10B981',
            secondary: '#FFFFFF',
          },
        },
        error: {
          iconTheme: {
            primary: '#EF4444',
            secondary: '#FFFFFF',
          },
        },
      }} />

      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/sales" element={<ProtectedRoute><Sales /></ProtectedRoute>} />
        <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
        <Route path="/inventory" element={<ProtectedRoute><Inventory /></ProtectedRoute>} />
        <Route path="/expenses" element={<ProtectedRoute><Expenses /></ProtectedRoute>} />
        <Route path="/assistant" element={<ProtectedRoute><AIAssistant /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;
