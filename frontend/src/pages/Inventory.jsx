import React, { useState, useEffect } from 'react';
import api from '../services/api';
import toast from 'react-hot-toast';
import { AlertTriangle, Loader2, Plus, Truck, PackagePlus } from 'lucide-react';
import AddProductModal from '../components/AddProductModal';
import AddRestockModal from '../components/AddRestockModal';

const Inventory = () => {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [isAddProductModalOpen, setIsAddProductModalOpen] = useState(false);
  
  const [isRestockModalOpen, setIsRestockModalOpen] = useState(false);
  const [productToRestock, setProductToRestock] = useState(null);

  const fetchInventory = async () => {
    setLoading(true);
    try {
      const res = await api.get('/analytics/all-products');
      if (res.data && res.data.data) {
        setInventory(res.data.data);
      }
    } catch (error) {
      console.error("Error fetching inventory:", error);
      toast.error("Failed to load inventory");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInventory();
  }, []);

  const handleToggleStatus = async (product) => {
    try {
      const newStatus = product.is_on_the_way ? 0 : 1;
      await api.put(`/inventory/products/${product.id}/status?is_on_the_way=${newStatus}`);
      toast.success(newStatus ? "Marked as on the way" : "Status reset");
      fetchInventory();
    } catch (error) {
      console.error("Error updating status:", error);
      toast.error("Failed to update status");
    }
  };

  const handleOpenRestock = (product) => {
    setProductToRestock(product);
    setIsRestockModalOpen(true);
  };

  const getStatusBadge = (product) => {
    if (product.is_on_the_way) {
      return (
        <button 
          onClick={() => handleToggleStatus(product)}
          className="flex items-center gap-1.5 px-3 py-1 bg-blue-50 text-blue-600 rounded-full text-xs font-bold hover:bg-blue-100 transition-colors"
          title="Click to reset status"
        >
          <Truck size={14} /> On The Way
        </button>
      );
    }
    
    if (product.current_stock < 10) {
      return (
        <button 
          onClick={() => handleToggleStatus(product)}
          className="flex items-center gap-1.5 px-3 py-1 bg-red-50 text-red-600 rounded-full text-xs font-bold hover:bg-red-100 transition-colors"
          title="Click to mark as on the way"
        >
          <AlertTriangle size={14} /> Low Stock
        </button>
      );
    }

    return (
      <span className="flex items-center gap-1.5 px-3 py-1 bg-green-50 text-green-600 rounded-full text-xs font-bold">
        In Stock
      </span>
    );
  };

  if (loading && inventory.length === 0) {
    return (
      <div className="flex h-full items-center justify-center min-h-[400px]">
        <Loader2 className="animate-spin text-accent w-10 h-10" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6 relative animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-text-main">Inventory Management</h1>
        <button 
          onClick={() => setIsAddProductModalOpen(true)}
          className="bg-accent text-sidebar px-4 py-2 rounded-lg font-bold hover:opacity-90 transition-opacity flex items-center gap-2"
        >
          <Plus size={20} />
          Add Product
        </button>
      </div>
      
      <div className="bg-card rounded-xl shadow-md border border-slate-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-text-main">Current Stock Levels</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-50">
              <tr className="text-text-main/70 text-sm">
                <th className="px-6 py-4 font-medium">Product Code</th>
                <th className="px-6 py-4 font-medium">Product Name</th>
                <th className="px-6 py-4 font-medium">Category</th>
                <th className="px-6 py-4 font-medium">Price</th>
                <th className="px-6 py-4 font-medium">Current Stock</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-text-main">
              {inventory.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 font-mono font-medium text-slate-500">{item.product_code || 'N/A'}</td>
                  <td className="px-6 py-4 font-medium">{item.name}</td>
                  <td className="px-6 py-4">
                    <span className="px-2.5 py-1 bg-slate-100 text-slate-600 rounded-md text-xs font-medium">
                      {item.category}
                    </span>
                  </td>
                  <td className="px-6 py-4">₹{item.price.toLocaleString()}</td>
                  <td className="px-6 py-4 font-bold text-lg">{item.current_stock}</td>
                  <td className="px-6 py-4">
                    {getStatusBadge(item)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button 
                      onClick={() => handleOpenRestock(item)}
                      className="text-sidebar hover:text-accent hover:bg-sidebar px-3 py-1.5 rounded-lg transition-colors text-sm font-semibold flex items-center justify-end gap-1.5 ml-auto"
                    >
                      <PackagePlus size={16}/> Restock
                    </button>
                  </td>
                </tr>
              ))}
              {inventory.length === 0 && (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-text-main/50">
                    No products found in inventory.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      
      <AddProductModal 
        isOpen={isAddProductModalOpen} 
        onClose={() => setIsAddProductModalOpen(false)} 
        onSuccess={fetchInventory}
      />
      
      <AddRestockModal
        isOpen={isRestockModalOpen}
        onClose={() => setIsRestockModalOpen(false)}
        onSuccess={fetchInventory}
        product={productToRestock}
      />
    </div>
  );
};

export default Inventory;
