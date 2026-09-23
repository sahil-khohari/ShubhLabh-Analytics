import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer, Legend } from 'recharts';
import { Users, Receipt, AlertCircle, Plus, Loader2, Edit2, Trash2 } from 'lucide-react';
import AddExpenseModal from '../components/AddExpenseModal';
import AddEmployeeModal from '../components/AddEmployeeModal';
import toast from 'react-hot-toast';

const COLORS = ['#FFD369', '#FF8B8B', '#60A5FA', '#34D399', '#A78BFA', '#FBBF24'];

const Expenses = () => {
  const [expenses, setExpenses] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [isExpenseModalOpen, setIsExpenseModalOpen] = useState(false);
  const [expenseToEdit, setExpenseToEdit] = useState(null);
  const [isEmployeeModalOpen, setIsEmployeeModalOpen] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [expRes, empRes, sumRes] = await Promise.all([
        api.get('/expenses'),
        api.get('/employees'),
        api.get('/expenses/summary')
      ]);
      setExpenses(expRes.data.data);
      setEmployees(empRes.data.data);
      setSummary(sumRes.data.data);
    } catch (error) {
      console.error("Failed to fetch expense data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDeleteExpense = async (expenseId) => {
    if (!window.confirm("Are you sure you want to delete this expense?")) return;
    try {
      await api.delete(`/expenses/${expenseId}`);
      toast.success("Expense deleted successfully");
      fetchData();
    } catch (error) {
      console.error("Failed to delete expense", error);
      toast.error("Failed to delete expense");
    }
  };

  const openEditExpenseModal = (expense) => {
    setExpenseToEdit(expense);
    setIsExpenseModalOpen(true);
  };

  const openAddExpenseModal = () => {
    setExpenseToEdit(null);
    setIsExpenseModalOpen(true);
  };

  const chartData = summary ? [
    { name: 'Net Profit', value: Math.max(0, summary.true_net_profit) },
    ...Object.entries(summary.expenses_breakdown).map(([k, v]) => ({ name: k, value: v }))
  ] : [];

  if (loading) return <div className="p-8 flex justify-center"><Loader2 size={32} className="animate-spin text-accent" /></div>;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-text-main">Expenses & Payroll</h1>
      </div>

      {/* Top Section: Analysis */}
      <div className="bg-card rounded-2xl shadow-md border border-slate-200 p-6 flex flex-col lg:flex-row gap-8">
        <div className="flex-1 space-y-6">
          <h2 className="text-xl font-bold text-text-main">True Net Profit Analysis</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
              <p className="text-sm font-medium text-text-main/70">Total Sales Profit</p>
              <p className="text-2xl font-bold text-text-main mt-1">₹{summary?.total_sales_profit?.toLocaleString()}</p>
            </div>
            <div className="p-4 bg-red-50 rounded-xl border border-red-100">
              <p className="text-sm font-medium text-red-600">Total Expenses</p>
              <p className="text-2xl font-bold text-red-700 mt-1">₹{summary?.total_expenses?.toLocaleString()}</p>
            </div>
          </div>
          <div className="p-5 bg-sidebar rounded-xl">
            <p className="text-sm font-medium text-slate-300">True Net Profit (After Overhead)</p>
            <p className="text-3xl font-bold text-accent mt-1">₹{summary?.true_net_profit?.toLocaleString()}</p>
          </div>
        </div>
        
        <div className="flex-1 h-64 relative">
          {summary && summary.total_sales_profit > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={110}
                  paddingAngle={3}
                  dataKey="value"
                  stroke="none"
                >
                  {chartData.map((entry, index) => {
                    let color = '#EF4444';
                    if (entry.name === 'Net Profit') color = '#10B981';
                    else {
                      const expenseColors = ['#EF4444', '#DC2626', '#B91C1C', '#991B1B', '#7F1D1D'];
                      color = expenseColors[(index - 1) % expenseColors.length];
                    }
                    return <Cell key={`cell-${index}`} fill={color} stroke="none" />
                  })}
                </Pie>
                <RechartsTooltip formatter={(value) => `₹${value.toLocaleString()}`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-400">
              Not enough data for chart
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Expenses List */}
        <div className="bg-card rounded-2xl shadow-md border border-slate-200 overflow-hidden flex flex-col">
          <div className="p-6 border-b border-slate-200 flex justify-between items-center bg-slate-50">
            <h2 className="text-lg font-bold text-text-main flex items-center gap-2">
              <Receipt className="text-accent" size={20} /> Operational Expenses
            </h2>
            <button 
              onClick={openAddExpenseModal}
              className="bg-sidebar text-white px-3 py-1.5 rounded-lg text-sm font-semibold hover:bg-sidebar/90 transition-colors flex items-center gap-1"
            >
              <Plus size={16} /> Add Expense
            </button>
          </div>
          <div className="p-0 overflow-y-auto max-h-[500px]">
            {expenses.length === 0 ? (
              <div className="p-8 text-center text-slate-500">No expenses logged yet.</div>
            ) : (
              <table className="w-full text-left">
                <thead className="bg-slate-50 sticky top-0 text-sm text-text-main/70">
                  <tr>
                    <th className="px-6 py-3 font-medium">Date</th>
                    <th className="px-6 py-3 font-medium">Category</th>
                    <th className="px-6 py-3 font-medium">Amount</th>
                    <th className="px-6 py-3 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-sm">
                  {expenses.map(exp => (
                    <tr key={exp.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 text-slate-500">{new Date(exp.timestamp).toLocaleDateString()}</td>
                      <td className="px-6 py-4 font-medium text-text-main">
                        <div>{exp.category}</div>
                        <div className="text-xs text-slate-500 truncate max-w-[120px]" title={exp.description}>{exp.description}</div>
                      </td>
                      <td className="px-6 py-4 font-semibold text-red-600">₹{exp.amount.toLocaleString()}</td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <button 
                            onClick={() => openEditExpenseModal(exp)}
                            className="p-1.5 text-text-main/40 hover:text-blue-500 hover:bg-blue-50 rounded-full transition-colors"
                            title="Edit Expense"
                          >
                            <Edit2 size={16} />
                          </button>
                          <button 
                            onClick={() => handleDeleteExpense(exp.id)}
                            className="p-1.5 text-text-main/40 hover:text-red-500 hover:bg-red-50 rounded-full transition-colors"
                            title="Delete Expense"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Employees List */}
        <div className="bg-card rounded-2xl shadow-md border border-slate-200 overflow-hidden flex flex-col">
          <div className="p-6 border-b border-slate-200 flex justify-between items-center bg-slate-50">
            <h2 className="text-lg font-bold text-text-main flex items-center gap-2">
              <Users className="text-accent" size={20} /> Employee Roster
            </h2>
            <button 
              onClick={() => setIsEmployeeModalOpen(true)}
              className="bg-sidebar text-white px-3 py-1.5 rounded-lg text-sm font-semibold hover:bg-sidebar/90 transition-colors flex items-center gap-1"
            >
              <Plus size={16} /> Onboard
            </button>
          </div>
          <div className="p-0 overflow-y-auto max-h-[500px]">
            {employees.length === 0 ? (
              <div className="p-8 text-center text-slate-500">No employees onboarded yet.</div>
            ) : (
              <table className="w-full text-left">
                <thead className="bg-slate-50 sticky top-0 text-sm text-text-main/70">
                  <tr>
                    <th className="px-6 py-3 font-medium">Name</th>
                    <th className="px-6 py-3 font-medium">Role</th>
                    <th className="px-6 py-3 font-medium">Monthly Salary</th>
                    <th className="px-6 py-3 font-medium">Joined</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-sm">
                  {employees.map(emp => (
                    <tr key={emp.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 font-medium text-text-main">{emp.name}</td>
                      <td className="px-6 py-4 text-slate-600">{emp.role}</td>
                      <td className="px-6 py-4 font-semibold text-text-main">₹{emp.salary_amount.toLocaleString()}</td>
                      <td className="px-6 py-4 text-slate-500">{new Date(emp.join_date).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>

      <AddExpenseModal isOpen={isExpenseModalOpen} onClose={() => setIsExpenseModalOpen(false)} onSuccess={fetchData} editExpense={expenseToEdit} />
      <AddEmployeeModal isOpen={isEmployeeModalOpen} onClose={() => setIsEmployeeModalOpen(false)} onSuccess={fetchData} />
    </div>
  );
};

export default Expenses;
