import React, { useState, useEffect } from 'react';
import { X, Loader2, UserPlus } from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';

const AddEmployeeModal = ({ isOpen, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    role: '',
    salary_amount: ''
  });

  useEffect(() => {
    if (isOpen) {
      setFormData({
        name: '',
        role: '',
        salary_amount: ''
      });
    }
  }, [isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.role || !formData.salary_amount) {
      toast.error("Please fill all fields");
      return;
    }

    setLoading(true);
    try {
      await api.post('/employees', {
        name: formData.name,
        role: formData.role,
        salary_amount: parseFloat(formData.salary_amount),
        join_date: formData.join_date || new Date().toISOString().split('T')[0]
      });
      toast.success("Employee onboarded successfully!");
      onSuccess();
      onClose();
    } catch (error) {
      console.error("Failed to add employee", error);
      toast.error("Failed to add employee");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-sidebar/40 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-200">
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-sidebar">
          <h2 className="text-xl font-bold text-canvas flex items-center gap-2">
            <UserPlus className="text-accent" size={24} />
            Onboard New Employee
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <X size={24} />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-sidebar mb-1">Employee Name</label>
              <input 
                type="text"
                placeholder="e.g. Ramesh Singh"
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sidebar mb-1">Role</label>
              <input 
                type="text"
                placeholder="e.g. Cashier"
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
                value={formData.role}
                onChange={(e) => setFormData({...formData, role: e.target.value})}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sidebar mb-1">Monthly Salary (₹)</label>
              <input 
                type="number"
                min="0"
                step="0.01"
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
                value={formData.salary_amount}
                onChange={(e) => setFormData({...formData, salary_amount: e.target.value})}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sidebar mb-1">Payment Date</label>
              <input 
                type="date"
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
                value={formData.join_date || new Date().toISOString().split('T')[0]}
                onChange={(e) => setFormData({...formData, join_date: e.target.value})}
                required
              />
            </div>
          </div>

          <div className="pt-6 flex gap-3">
            <button type="button" onClick={onClose} className="flex-1 py-2.5 rounded-lg border border-slate-300 text-sidebar font-medium hover:bg-slate-50 transition-colors">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="flex-1 py-2.5 rounded-lg bg-accent text-sidebar font-bold hover:opacity-90 transition-colors flex justify-center items-center gap-2">
              {loading ? <Loader2 size={18} className="animate-spin" /> : null}
              {loading ? 'Onboarding...' : 'Onboard Employee'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddEmployeeModal;
