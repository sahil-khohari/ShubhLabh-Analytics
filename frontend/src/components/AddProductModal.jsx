import React, { useState, useEffect } from 'react';
import { X, Loader2, PackagePlus } from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';

const AddProductModal = ({ isOpen, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    purchase_price: '',
    selling_price: '',
    current_stock: ''
  });

  // Reset form when opened
  useEffect(() => {
    if (isOpen) {
      setFormData({
        name: '',
        category: '',
        purchase_price: '',
        selling_price: '',
        current_stock: ''
      });
    }
  }, [isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.category || !formData.purchase_price || !formData.selling_price || !formData.current_stock) {
      toast.error("Please fill all fields");
      return;
    }

    setLoading(true);
    try {
      await api.post('/inventory/products', {
        name: formData.name,
        category: formData.category,
        purchase_price: parseFloat(formData.purchase_price),
        selling_price: parseFloat(formData.selling_price),
        current_stock: parseInt(formData.current_stock)
      });
      
      toast.success("Product added successfully!");
      onSuccess();
      onClose();
    } catch (error) {
      console.error("Failed to add product", error);
      toast.error(error.response?.data?.detail || "Failed to add product");
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
            <PackagePlus className="text-accent" size={24} />
            Add New Product
          </h2>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors"
          >
            <X size={24} />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-sidebar mb-1">Product Name</label>
              <input 
                type="text"
                placeholder="e.g. Wireless Mouse"
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sidebar mb-1">Category</label>
              <input 
                type="text"
                placeholder="e.g. Electronics"
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
                value={formData.category}
                onChange={(e) => setFormData({...formData, category: e.target.value})}
                required
              />
            </div>

            <div className="flex gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-sidebar mb-1">Purchase Price (₹)</label>
                <input 
                  type="number"
                  min="0"
                  step="0.01"
                  className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
                  value={formData.purchase_price}
                  onChange={(e) => setFormData({...formData, purchase_price: e.target.value})}
                  required
                />
              </div>
              <div className="flex-1">
                <label className="block text-sm font-medium text-sidebar mb-1">Selling Price (₹)</label>
                <input 
                  type="number"
                  min="0"
                  step="0.01"
                  className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
                  value={formData.selling_price}
                  onChange={(e) => setFormData({...formData, selling_price: e.target.value})}
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-sidebar mb-1">Initial Stock Quantity</label>
              <input 
                type="number"
                min="0"
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
                value={formData.current_stock}
                onChange={(e) => setFormData({...formData, current_stock: e.target.value})}
                required
              />
            </div>
          </div>

          <div className="pt-6 flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 rounded-lg border border-slate-300 text-sidebar font-medium hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-2.5 rounded-lg bg-accent text-sidebar font-bold hover:opacity-90 transition-colors flex justify-center items-center gap-2"
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : null}
              {loading ? 'Adding...' : 'Add Product'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddProductModal;
