import React, { useState, useEffect } from 'react';
import api from '../services/api';
import toast from 'react-hot-toast';
import { Loader2, Trash2, Edit2 } from 'lucide-react';
import AddSaleModal from '../components/AddSaleModal';

const Sales = () => {
  const [products, setProducts] = useState([]);
  const [sales, setSales] = useState([]);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [loadingSales, setLoadingSales] = useState(false);
  const [saving, setSaving] = useState(false);
  const [filter, setFilter] = useState('today'); // 'today', 'weekly', 'monthly'
  
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [saleToEdit, setSaleToEdit] = useState(null);

  const [formData, setFormData] = useState({
    product_id: '',
    quantity: 1,
    sale_date: new Date().toISOString().split('T')[0],
    custom_selling_price: ''
  });

  useEffect(() => {
    fetchProducts();
    fetchSales();
  }, [filter]);

  const fetchProducts = async () => {
    setLoadingProducts(true);
    try {
      const res = await api.get(`/analytics/all-products`);
      if (res.data && res.data.data) {
        setProducts(res.data.data);
      }
    } catch (error) {
      console.error("Failed to fetch products", error);
    } finally {
      setLoadingProducts(false);
    }
  };

  const fetchSales = async () => {
    setLoadingSales(true);
    try {
      const res = await api.get(`/sales?filter=${filter}`);
      if (res.data && res.data.data) {
        setSales(res.data.data);
      }
    } catch (error) {
      console.error("Failed to fetch sales", error);
      toast.error("Failed to load sales history");
    } finally {
      setLoadingSales(false);
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
      await api.post('/sales', {
        product_id: parseInt(formData.product_id),
        quantity: parseInt(formData.quantity),
        sale_date: formData.sale_date,
        custom_selling_price: formData.custom_selling_price ? parseFloat(formData.custom_selling_price) : null
      });
      toast.success("Sale logged successfully!");
      setFormData({
        product_id: '',
        quantity: 1,
        sale_date: new Date().toISOString().split('T')[0],
        custom_selling_price: ''
      });
      fetchSales();
    } catch (error) {
      console.error("Failed to add sale", error);
      toast.error(error.response?.data?.detail || "Failed to add sale. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (saleId) => {
    if (!window.confirm("Are you sure you want to delete this transaction? This will refund inventory.")) return;
    
    try {
      await api.delete(`/sales/${saleId}`);
      toast.success("Sale deleted successfully");
      fetchSales();
    } catch (error) {
      console.error("Failed to delete sale", error);
      toast.error("Failed to delete sale");
    }
  };
  
  const openEditModal = (sale) => {
    setSaleToEdit(sale);
    setIsEditModalOpen(true);
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-text-main">Sales Management</h1>
      </div>

      {/* Record New Sale Form */}
      <div className="bg-card rounded-xl shadow-md border border-slate-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-sidebar">
          <h2 className="text-lg font-bold text-canvas">Record New Sale</h2>
        </div>
        <form onSubmit={handleSubmit} className="p-6 flex flex-col md:flex-row gap-4 items-end flex-wrap">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-sidebar mb-1">Product</label>
            {loadingProducts ? (
              <div className="flex items-center gap-2 text-sm text-sidebar/70 py-2">
                <Loader2 size={16} className="animate-spin" /> Loading products...
              </div>
            ) : (
              <select 
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
                value={formData.product_id}
                onChange={handleProductChange}
                required
              >
                <option value="" disabled>Select a product</option>
                {products.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.product_code ? `[${p.product_code}] ` : ''}{p.name}
                  </option>
                ))}
              </select>
            )}
          </div>
          
          <div className="w-full md:w-32">
            <label className="block text-sm font-medium text-sidebar mb-1">Price (₹)</label>
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

          <div className="w-full md:w-28">
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

          <div className="w-full md:w-40">
            <label className="block text-sm font-medium text-sidebar mb-1">Sale Date</label>
            <input 
              type="date"
              className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sidebar focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent bg-white"
              value={formData.sale_date}
              onChange={(e) => setFormData({...formData, sale_date: e.target.value})}
              required
            />
          </div>

          <button
            type="submit"
            disabled={saving || loadingProducts}
            className="w-full md:w-auto py-2.5 px-6 rounded-lg bg-accent text-sidebar font-bold hover:opacity-90 transition-colors flex justify-center items-center gap-2"
          >
            {saving ? <Loader2 size={18} className="animate-spin" /> : null}
            {saving ? 'Recording...' : 'Record Sale'}
          </button>
        </form>
      </div>

      {/* Transactions Table */}
      <div className="bg-card rounded-xl shadow-md border border-slate-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <h2 className="text-lg font-semibold text-text-main">Transaction History</h2>
          <div className="flex bg-slate-100 p-1 rounded-lg">
            {['today', 'weekly', 'monthly'].map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-1.5 text-sm font-medium rounded-md capitalize transition-colors ${
                  filter === f 
                    ? 'bg-white text-sidebar shadow-sm border border-slate-200' 
                    : 'text-text-main/60 hover:text-sidebar'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        <div className="relative">
          {loadingSales && (
            <div className="absolute inset-0 bg-white/60 backdrop-blur-sm z-10 flex items-center justify-center min-h-[200px]">
              <Loader2 className="animate-spin text-accent w-8 h-8" />
            </div>
          )}
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[600px]">
              <thead>
                <tr className="bg-slate-50 text-text-main/70 text-sm">
                  <th className="px-6 py-3 font-medium">Date</th>
                  <th className="px-6 py-3 font-medium">Product</th>
                  <th className="px-6 py-3 font-medium">Qty</th>
                  <th className="px-6 py-3 font-medium">Price/Item</th>
                  <th className="px-6 py-3 font-medium">Total Price</th>
                  <th className="px-6 py-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-text-main">
                {sales.map((sale) => (
                  <tr key={sale.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">{sale.sale_date}</td>
                    <td className="px-6 py-4 font-medium">{sale.product_name}</td>
                    <td className="px-6 py-4">{sale.quantity}</td>
                    <td className="px-6 py-4">₹{sale.selling_price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                    <td className="px-6 py-4 font-semibold">₹{sale.total_price.toLocaleString()}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button 
                          onClick={() => openEditModal(sale)}
                          className="p-2 text-text-main/40 hover:text-blue-500 hover:bg-blue-50 rounded-full transition-colors"
                          title="Edit Sale"
                        >
                          <Edit2 size={18} />
                        </button>
                        <button 
                          onClick={() => handleDelete(sale.id)}
                          className="p-2 text-text-main/40 hover:text-red-500 hover:bg-red-50 rounded-full transition-colors"
                          title="Delete Sale"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {sales.length === 0 && !loadingSales && (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center text-text-main/50">
                      No sales found for the selected time period.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <AddSaleModal 
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        onSuccess={fetchSales}
        editSale={saleToEdit}
      />
    </div>
  );
};

export default Sales;
