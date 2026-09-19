import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if token exists in localStorage on mount
    const token = localStorage.getItem('token');
    if (token) {
      // In a real app, you would validate the token with the backend here.
      // For now, we'll just assume they are logged in if they have a token.
      setUser({ token });
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const formData = new FormData();
    // OAuth2PasswordBearer expects form data, or we can adjust backend to accept JSON.
    // Wait, in auth.py we used `user_data: UserLogin` which expects JSON!
    // Let's send JSON.
    const res = await api.post('/auth/login', { email, password });
    const { access_token } = res.data;
    localStorage.setItem('token', access_token);
    setUser({ token: access_token });
    return true;
  };

  const register = async (name, email, password) => {
    await api.post('/auth/register', { name, email, password });
    return await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
