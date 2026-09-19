import React, { useState } from 'react';
import api from '../services/api';
import toast from 'react-hot-toast';
import { X, Loader2 } from 'lucide-react';

const AddRestockModal = ({ isOpen, onClose, onSuccess, product }) => {
  const [loading, setLoading] = useState(false);
  const [quantity, setQuantity] = useState(1);
  const [restockDate, setRestockDate] = useState(new Date().toISOString().split('T')[0]);

  if (!isOpen || !product) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (quantity <= 0) {
      toast.error("Quantity must be at least 1");
      return;
    }

    setLoading(true);
    try {
      await api.post('/inventory/restock', {
        product_id: product.id,
        quantity: parseInt(quantity),
        restock_date: restockDate
      });
      toast.success("Product restocked successfully!");
      onSuccess();
      onClose();
      setQuantity(1); // Reset form
    } catch (error) {
      console.error("Failed to restock product", error);
      toast.error("Failed to restock product. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-sidebar/50 backdrop-blur-sm">
      <div className="bg-card w-full max-w-md rounded-2xl shadow-xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-sidebar">
          <h2 className="text-lg font-bold text-canvas">Restock Product</h2>
          <button 
            onClick={onClose}
            className="text-canvas/70 hover:text-accent transition-colors"
          >
            <X size={20} />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-sidebar mb-1">Product</label>
            <input 
              type="text"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-slate-500 bg-slate-50 cursor-not-allowed"
              value={product.name}
              readOnly
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-sidebar mb-1">Current Stock</label>
            <input 
              type="text"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-slate-500 bg-slate-50 cursor-not-allowed"
              value={product.current_stock}
              readOnly
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-sidebar mb-1">Add Quantity</label>
            <input 
              type="number"
              min="1"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-sidebar mb-1">Payment Date</label>
            <input 
              type="date"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
              value={restockDate}
              onChange={(e) => setRestockDate(e.target.value)}
              required
            />
          </div>

          <div className="pt-4 flex gap-3">
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
              {loading ? 'Restocking...' : 'Restock'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddRestockModal;
