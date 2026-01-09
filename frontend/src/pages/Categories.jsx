import { useState, useEffect } from 'react';
import { categoriesAPI } from '../services/api';
import { Plus, Edit, Trash2, X, Loader2 } from 'lucide-react';

const COLORS = [
  '#ef4444', '#f97316', '#eab308', '#22c55e', '#10b981',
  '#06b6d4', '#3b82f6', '#6366f1', '#8b5cf6', '#ec4899',
];

export default function Categories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    type: 'expense',
    color: '#6366f1',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('expense');

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await categoriesAPI.getAll();
      setCategories(response.data);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    } finally {
      setLoading(false);
    }
  };

  const openModal = (category = null) => {
    if (category) {
      setEditingCategory(category);
      setFormData({
        name: category.name,
        type: category.type,
        color: category.color,
      });
    } else {
      setEditingCategory(null);
      setFormData({
        name: '',
        type: activeTab,
        color: '#6366f1',
      });
    }
    setError('');
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingCategory(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      if (editingCategory) {
        await categoriesAPI.update(editingCategory.id, {
          name: formData.name,
          color: formData.color,
        });
      } else {
        await categoriesAPI.create(formData);
      }

      closeModal();
      fetchCategories();
    } catch (err) {
      setError(err.response?.data?.detail || 'Không thể lưu danh mục');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Bạn có chắc chắn muốn xóa danh mục này?')) return;

    try {
      await categoriesAPI.delete(id);
      fetchCategories();
    } catch (error) {
      console.error('Failed to delete:', error);
      alert('Không thể xóa danh mục đang được sử dụng');
    }
  };

  const filteredCategories = categories.filter((c) => c.type === activeTab);
  const systemCategories = filteredCategories.filter((c) => c.user_id === null);
  const userCategories = filteredCategories.filter((c) => c.user_id !== null);

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
        <h1 className="text-2xl font-bold text-slate-900">Danh mục</h1>
        <button onClick={() => openModal()} className="btn btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Thêm danh mục
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('expense')}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'expense'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          Danh mục chi tiêu
        </button>
        <button
          onClick={() => setActiveTab('income')}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'income'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-slate-600 hover:text-slate-900'
          }`}
        >
          Danh mục thu nhập
        </button>
      </div>

      {/* System Categories */}
      {systemCategories.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-slate-500 mb-3">Danh mục mặc định</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {systemCategories.map((cat) => (
              <div
                key={cat.id}
                className="card flex items-center gap-3"
                style={{ borderLeftWidth: '4px', borderLeftColor: cat.color }}
              >
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
                  style={{ backgroundColor: cat.color }}
                >
                  {cat.name.charAt(0)}
                </div>
                <span className="text-sm font-medium text-slate-700">{cat.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* User Categories */}
      <div>
        <h2 className="text-sm font-medium text-slate-500 mb-3">Danh mục của bạn</h2>
        {userCategories.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {userCategories.map((cat) => (
              <div
                key={cat.id}
                className="card flex items-center justify-between"
                style={{ borderLeftWidth: '4px', borderLeftColor: cat.color }}
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
                    style={{ backgroundColor: cat.color }}
                  >
                    {cat.name.charAt(0)}
                  </div>
                  <span className="text-sm font-medium text-slate-700">{cat.name}</span>
                </div>
                <div className="flex gap-1">
                  <button
                    onClick={() => openModal(cat)}
                    className="p-1 text-slate-400 hover:text-primary-600 transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(cat.id)}
                    className="p-1 text-slate-400 hover:text-red-600 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-slate-500 bg-slate-50 rounded-lg">
            Chưa có danh mục tùy chỉnh. Nhấn "Thêm danh mục" để tạo mới.
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
            <div className="flex items-center justify-between p-4 border-b border-slate-200">
              <h2 className="text-lg font-semibold">
                {editingCategory ? 'Sửa danh mục' : 'Thêm danh mục'}
              </h2>
              <button onClick={closeModal} className="p-1 hover:bg-slate-100 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-4 space-y-4">
              {error && (
                <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">{error}</div>
              )}

              <div>
                <label className="label">Tên danh mục</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="input"
                  placeholder="Tên danh mục"
                  required
                />
              </div>

              {!editingCategory && (
                <div>
                  <label className="label">Loại</label>
                  <div className="flex rounded-lg overflow-hidden border border-slate-200">
                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, type: 'expense' })}
                      className={`flex-1 py-2 text-sm font-medium transition-colors ${
                        formData.type === 'expense'
                          ? 'bg-red-500 text-white'
                          : 'bg-white text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      Chi tiêu
                    </button>
                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, type: 'income' })}
                      className={`flex-1 py-2 text-sm font-medium transition-colors ${
                        formData.type === 'income'
                          ? 'bg-green-500 text-white'
                          : 'bg-white text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      Thu nhập
                    </button>
                  </div>
                </div>
              )}

              <div>
                <label className="label">Màu sắc</label>
                <div className="flex flex-wrap gap-2">
                  {COLORS.map((color) => (
                    <button
                      key={color}
                      type="button"
                      onClick={() => setFormData({ ...formData, color })}
                      className={`w-8 h-8 rounded-full border-2 transition-all ${
                        formData.color === color
                          ? 'border-slate-900 scale-110'
                          : 'border-transparent'
                      }`}
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
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
