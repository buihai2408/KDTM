import { useState, useEffect } from 'react';
import { budgetsAPI, categoriesAPI } from '../services/api';
import { Plus, Edit, Trash2, X, Loader2, AlertTriangle, CheckCircle } from 'lucide-react';

function formatCurrency(amount) {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(amount);
}

export default function Budgets() {
  const [budgetStatus, setBudgetStatus] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingBudget, setEditingBudget] = useState(null);
  const [formData, setFormData] = useState({
    category_id: '',
    amount: '',
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear(),
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const currentMonth = new Date().getMonth() + 1;
  const currentYear = new Date().getFullYear();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statusRes, catRes] = await Promise.all([
        budgetsAPI.getStatus(currentMonth, currentYear),
        categoriesAPI.getAll('expense'),
      ]);
      setBudgetStatus(statusRes.data);
      setCategories(catRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const openModal = (budget = null) => {
    if (budget) {
      setEditingBudget(budget);
      setFormData({
        category_id: budget.category_id,
        amount: budget.budget_amount,
        month: budget.month,
        year: budget.year,
      });
    } else {
      setEditingBudget(null);
      const usedCategoryIds = budgetStatus.map((b) => b.category_id);
      const availableCategories = categories.filter((c) => !usedCategoryIds.includes(c.id));
      setFormData({
        category_id: availableCategories[0]?.id || '',
        amount: '',
        month: currentMonth,
        year: currentYear,
      });
    }
    setError('');
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingBudget(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      if (editingBudget) {
        await budgetsAPI.update(editingBudget.id, {
          amount: parseFloat(formData.amount),
        });
      } else {
        await budgetsAPI.create({
          category_id: parseInt(formData.category_id),
          amount: parseFloat(formData.amount),
          month: parseInt(formData.month),
          year: parseInt(formData.year),
        });
      }

      closeModal();
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Không thể lưu ngân sách');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Bạn có chắc chắn muốn xóa ngân sách này?')) return;

    try {
      await budgetsAPI.delete(id);
      fetchData();
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'exceeded':
        return 'bg-red-500';
      case 'warning':
        return 'bg-yellow-500';
      default:
        return 'bg-green-500';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'exceeded':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      default:
        return <CheckCircle className="w-5 h-5 text-green-500" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'exceeded':
        return 'Vượt ngân sách';
      case 'warning':
        return 'Cảnh báo';
      default:
        return 'An toàn';
    }
  };

  const usedCategoryIds = budgetStatus.map((b) => b.category_id);
  const availableCategories = categories.filter(
    (c) => !usedCategoryIds.includes(c.id) || editingBudget?.category_id === c.id
  );

  const totalBudget = budgetStatus.reduce((sum, b) => sum + parseFloat(b.budget_amount), 0);
  const totalSpent = budgetStatus.reduce((sum, b) => sum + parseFloat(b.actual_spent), 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Ngân sách</h1>
        <button
          onClick={() => openModal()}
          disabled={availableCategories.length === 0}
          className="btn btn-primary flex items-center gap-2 disabled:opacity-50"
        >
          <Plus className="w-5 h-5" />
          Thêm ngân sách
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <p className="text-sm text-slate-600 mb-1">Tổng ngân sách</p>
          <p className="text-2xl font-bold text-slate-900">{formatCurrency(totalBudget)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-600 mb-1">Đã chi tiêu</p>
          <p className="text-2xl font-bold text-red-600">{formatCurrency(totalSpent)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-600 mb-1">Còn lại</p>
          <p
            className={`text-2xl font-bold ${
              totalBudget - totalSpent >= 0 ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {formatCurrency(totalBudget - totalSpent)}
          </p>
        </div>
      </div>

      {/* Budget List */}
      <div className="space-y-4">
        {budgetStatus.map((budget) => (
          <div key={budget.id} className="card">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                {getStatusIcon(budget.status)}
                <div>
                  <h3 className="font-semibold text-slate-900">{budget.category_name}</h3>
                  <p className="text-sm text-slate-500">
                    {formatCurrency(budget.actual_spent)} / {formatCurrency(budget.budget_amount)}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    budget.status === 'exceeded'
                      ? 'bg-red-100 text-red-700'
                      : budget.status === 'warning'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-green-100 text-green-700'
                  }`}
                >
                  {budget.usage_percentage}%
                </span>
                <button
                  onClick={() => openModal(budget)}
                  className="p-1 text-slate-400 hover:text-primary-600 transition-colors"
                >
                  <Edit className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDelete(budget.id)}
                  className="p-1 text-slate-400 hover:text-red-600 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-slate-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all ${getStatusColor(budget.status)}`}
                style={{ width: `${Math.min(budget.usage_percentage, 100)}%` }}
              />
            </div>

            <div className="flex justify-between mt-2 text-sm text-slate-600">
              <span>Còn lại: {formatCurrency(Math.max(budget.remaining, 0))}</span>
              {budget.remaining < 0 && (
                <span className="text-red-600">
                  Vượt {formatCurrency(Math.abs(budget.remaining))}
                </span>
              )}
            </div>
          </div>
        ))}

        {budgetStatus.length === 0 && (
          <div className="text-center py-12 text-slate-500">
            Chưa có ngân sách cho tháng này. Nhấn "Thêm ngân sách" để tạo mới.
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
            <div className="flex items-center justify-between p-4 border-b border-slate-200">
              <h2 className="text-lg font-semibold">
                {editingBudget ? 'Sửa ngân sách' : 'Thêm ngân sách'}
              </h2>
              <button onClick={closeModal} className="p-1 hover:bg-slate-100 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-4 space-y-4">
              {error && (
                <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">{error}</div>
              )}

              {!editingBudget && (
                <div>
                  <label className="label">Danh mục</label>
                  <select
                    value={formData.category_id}
                    onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                    className="input"
                    required
                  >
                    <option value="">Chọn danh mục</option>
                    {availableCategories.map((cat) => (
                      <option key={cat.id} value={cat.id}>
                        {cat.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {editingBudget && (
                <div>
                  <label className="label">Danh mục</label>
                  <input
                    type="text"
                    value={editingBudget.category_name}
                    className="input bg-slate-50"
                    disabled
                  />
                </div>
              )}

              <div>
                <label className="label">Số tiền ngân sách (VND)</label>
                <input
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  className="input"
                  placeholder="Nhập số tiền ngân sách"
                  min="1"
                  required
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button type="button" onClick={closeModal} className="flex-1 btn btn-secondary">
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 btn btn-primary flex items-center justify-center gap-2"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Đang lưu...
                    </>
                  ) : (
                    'Lưu'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
