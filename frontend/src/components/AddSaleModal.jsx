import React, { useState, useEffect } from 'react';
import api from '../services/api';
import toast from 'react-hot-toast';
import { X, Loader2 } from 'lucide-react';

const AddSaleModal = ({ isOpen, onClose, onSuccess, editSale = null }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  
  const [formData, setFormData] = useState({
    product_id: '',
    quantity: 1,
    sale_date: new Date().toISOString().split('T')[0],
    custom_selling_price: ''
  });

  useEffect(() => {
    if (isOpen) {
      fetchProducts();
      if (editSale) {
        setFormData({
          product_id: editSale.product_id,
          quantity: editSale.quantity,
          sale_date: editSale.sale_date,
          custom_selling_price: editSale.selling_price || ''
        });
      } else {
        setFormData({
          product_id: '',
          quantity: 1,
          sale_date: new Date().toISOString().split('T')[0],
          custom_selling_price: ''
        });
      }
    }
  }, [isOpen, editSale]);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/analytics/all-products`);
      if (res.data && res.data.data) {
        setProducts(res.data.data);
      }
    } catch (error) {
      console.error("Failed to fetch products for modal", error);
      toast.error("Failed to load products");
    } finally {
      setLoading(false);
    }
  };

  const handleProductChange = (e) => {
    const selectedProductId = e.target.value;
    const selectedProduct = products.find(p => p.id === parseInt(selectedProductId));
    setFormData({
      ...formData,
      product_id: selectedProductId,
      custom_selling_price: selectedProduct ? selectedProduct.price : ''
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.product_id) {
      toast.error("Please select a product");
      return;
    }
    if (formData.quantity <= 0) {
      toast.error("Quantity must be at least 1");
      return;
    }

    setSaving(true);
    try {
      const payload = {
        product_id: parseInt(formData.product_id),
        quantity: parseInt(formData.quantity),
        sale_date: formData.sale_date,
        custom_selling_price: formData.custom_selling_price ? parseFloat(formData.custom_selling_price) : null
      };

      if (editSale) {
        await api.put(`/sales/${editSale.id}`, payload);
        toast.success("Sale updated successfully!");
      } else {
        await api.post('/sales', payload);
        toast.success("Sale logged successfully!");
      }
      
      onSuccess();
      onClose();
    } catch (error) {
      console.error("Failed to save sale", error);
      toast.error("Failed to save sale. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-sidebar/50 backdrop-blur-sm">
      <div className="bg-card w-full max-w-md rounded-2xl shadow-xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-sidebar">
          <h2 className="text-lg font-bold text-canvas">{editSale ? 'Edit Sale' : 'Log New Sale'}</h2>
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
            {loading ? (
              <div className="flex items-center gap-2 text-sm text-sidebar/70">
                <Loader2 size={16} className="animate-spin" /> Loading products...
              </div>
            ) : (
              <select 
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white disabled:bg-slate-50 disabled:text-slate-500"
                value={formData.product_id}
                onChange={handleProductChange}
                required
                disabled={!!editSale} // Don't allow changing product on edit to simplify inventory logic
              >
                <option value="" disabled>Select a product</option>
                {products.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.product_code ? `[${p.product_code}] ` : ''}{p.name}
                  </option>
                ))}
              </select>
            )}
            {editSale && <p className="text-xs text-slate-500 mt-1">Product cannot be changed when editing.</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-sidebar mb-1">Selling Price (₹)</label>
            <input 
              type="number"
              min="0"
              step="0.01"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
              value={formData.custom_selling_price}
              onChange={(e) => setFormData({...formData, custom_selling_price: e.target.value})}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-sidebar mb-1">Quantity</label>
            <input 
              type="number"
              min="1"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
              value={formData.quantity}
              onChange={(e) => setFormData({...formData, quantity: e.target.value})}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-sidebar mb-1">Sale Date</label>
            <input 
              type="date"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
              value={formData.sale_date}
              onChange={(e) => setFormData({...formData, sale_date: e.target.value})}
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
              disabled={saving}
              className="flex-1 py-2.5 rounded-lg bg-accent text-sidebar font-bold hover:opacity-90 transition-colors flex justify-center items-center gap-2"
            >
              {saving ? <Loader2 size={18} className="animate-spin" /> : null}
              {saving ? 'Saving...' : (editSale ? 'Save Changes' : 'Add Sale')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddSaleModal;
