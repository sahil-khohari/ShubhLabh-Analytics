import React, { useState, useEffect } from 'react';
import { X, Loader2, Receipt } from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';

const AddExpenseModal = ({ isOpen, onClose, onSuccess, editExpense = null }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    category: '',
    amount: '',
    description: ''
  });

  useEffect(() => {
    if (isOpen) {
      if (editExpense) {
        setFormData({
          category: editExpense.category,
          amount: editExpense.amount,
          description: editExpense.description
        });
      } else {
        setFormData({
          category: '',
          amount: '',
          description: ''
        });
      }
    }
  }, [isOpen, editExpense]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.category || !formData.amount || !formData.description) {
      toast.error("Please fill all fields");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        category: formData.category,
        amount: parseFloat(formData.amount),
        description: formData.description,
        expense_date: formData.expense_date || new Date().toISOString().split('T')[0]
      };

      if (editExpense) {
        await api.put(`/expenses/${editExpense.id}`, payload);
        toast.success("Expense updated successfully!");
      } else {
        await api.post('/expenses', payload);
        toast.success("Expense logged successfully!");
      }
      
      onSuccess();
      onClose();
    } catch (error) {
      console.error("Failed to save expense", error);
      toast.error("Failed to save expense");
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
            <Receipt className="text-accent" size={24} />
            {editExpense ? 'Edit Operational Expense' : 'Log Operational Expense'}
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <X size={24} />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-sidebar mb-1">Expense Category</label>
              <select 
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
                value={formData.category}
                onChange={(e) => setFormData({...formData, category: e.target.value})}
                required
              >
                <option value="" disabled>Select a category</option>
                <option value="Restocking">Restocking</option>
                <option value="Utility Bill">Utility Bill</option>
                <option value="Salary">Salary</option>
                <option value="Marketing">Marketing</option>
                <option value="Maintenance">Maintenance</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-sidebar mb-1">Amount (₹)</label>
              <input 
                type="number"
                min="0"
                step="0.01"
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
                value={formData.amount}
                onChange={(e) => setFormData({...formData, amount: e.target.value})}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sidebar mb-1">Description</label>
              <textarea 
                rows="3"
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white resize-none"
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sidebar mb-1">Payment Date</label>
              <input 
                type="date"
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
                value={formData.expense_date || new Date().toISOString().split('T')[0]}
                onChange={(e) => setFormData({...formData, expense_date: e.target.value})}
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
              {loading ? 'Saving...' : (editExpense ? 'Save Changes' : 'Save Expense')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddExpenseModal;
