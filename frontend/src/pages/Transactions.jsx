import { useState, useEffect } from 'react';
import { transactionsAPI, categoriesAPI, walletsAPI } from '../services/api';
import { Plus, Edit, Trash2, X, Loader2 } from 'lucide-react';

function formatCurrency(amount) {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(amount);
}

export default function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [wallets, setWallets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState(null);
  const [formData, setFormData] = useState({
    type: 'expense',
    category_id: '',
    wallet_id: '',
    amount: '',
    description: '',
    transaction_date: new Date().toISOString().split('T')[0],
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [txRes, catRes, walRes] = await Promise.all([
        transactionsAPI.getAll({ limit: 100 }),
        categoriesAPI.getAll(),
        walletsAPI.getAll(),
      ]);
      setTransactions(txRes.data);
      setCategories(catRes.data);
      setWallets(walRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const openModal = (transaction = null) => {
    if (transaction) {
      setEditingTransaction(transaction);
      setFormData({
        type: transaction.type,
        category_id: transaction.category_id,
        wallet_id: transaction.wallet_id,
        amount: transaction.amount,
        description: transaction.description || '',
        transaction_date: transaction.transaction_date,
      });
    } else {
      setEditingTransaction(null);
      setFormData({
        type: 'expense',
        category_id: categories.find((c) => c.type === 'expense')?.id || '',
        wallet_id: wallets[0]?.id || '',
        amount: '',
        description: '',
        transaction_date: new Date().toISOString().split('T')[0],
      });
    }
    setError('');
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingTransaction(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      const data = {
        ...formData,
        amount: parseFloat(formData.amount),
        category_id: parseInt(formData.category_id),
        wallet_id: parseInt(formData.wallet_id),
      };

      if (editingTransaction) {
        await transactionsAPI.update(editingTransaction.id, data);
      } else {
        await transactionsAPI.create(data);
      }

      closeModal();
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Không thể lưu giao dịch');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Bạn có chắc chắn muốn xóa giao dịch này?')) return;

    try {
      await transactionsAPI.delete(id);
      fetchData();
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  };

  const filteredCategories = categories.filter((c) => c.type === formData.type);

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
        <h1 className="text-2xl font-bold text-slate-900">Giao dịch</h1>
        <button onClick={() => openModal()} className="btn btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Thêm giao dịch
        </button>
      </div>

      {/* Transactions List */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">Ngày</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">Danh mục</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">Ví</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">Mô tả</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-slate-600">Số tiền</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-slate-600">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="py-3 px-4 text-sm text-slate-600">
                    {new Date(tx.transaction_date).toLocaleDateString('vi-VN')}
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                      style={{
                        backgroundColor: `${tx.category_color}20`,
                        color: tx.category_color,
                      }}
                    >
                      {tx.category_name}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-slate-600">{tx.wallet_name}</td>
                  <td className="py-3 px-4 text-sm text-slate-600">{tx.description || '-'}</td>
                  <td
                    className={`py-3 px-4 text-sm font-medium text-right ${
                      tx.type === 'income' ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {tx.type === 'income' ? '+' : '-'}
                    {formatCurrency(tx.amount)}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => openModal(tx)}
                      className="p-1 text-slate-400 hover:text-primary-600 transition-colors"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(tx.id)}
                      className="p-1 text-slate-400 hover:text-red-600 transition-colors ml-2"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
              {transactions.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">
                    Chưa có giao dịch nào. Nhấn "Thêm giao dịch" để tạo mới.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
            <div className="flex items-center justify-between p-4 border-b border-slate-200">
              <h2 className="text-lg font-semibold">
                {editingTransaction ? 'Sửa giao dịch' : 'Thêm giao dịch'}
              </h2>
              <button onClick={closeModal} className="p-1 hover:bg-slate-100 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-4 space-y-4">
              {error && (
                <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">{error}</div>
              )}

              {/* Type Toggle */}
              <div className="flex rounded-lg overflow-hidden border border-slate-200">
                <button
                  type="button"
                  onClick={() => {
                    setFormData({ ...formData, type: 'expense', category_id: '' });
                  }}
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
                  onClick={() => {
                    setFormData({ ...formData, type: 'income', category_id: '' });
                  }}
                  className={`flex-1 py-2 text-sm font-medium transition-colors ${
                    formData.type === 'income'
                      ? 'bg-green-500 text-white'
                      : 'bg-white text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  Thu nhập
                </button>
              </div>

              <div>
                <label className="label">Danh mục</label>
                <select
                  value={formData.category_id}
                  onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                  className="input"
                  required
                >
                  <option value="">Chọn danh mục</option>
                  {filteredCategories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">Ví</label>
                <select
                  value={formData.wallet_id}
                  onChange={(e) => setFormData({ ...formData, wallet_id: e.target.value })}
                  className="input"
                  required
                >
                  <option value="">Chọn ví</option>
                  {wallets.map((wallet) => (
                    <option key={wallet.id} value={wallet.id}>
                      {wallet.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">Số tiền (VND)</label>
                <input
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  className="input"
                  placeholder="Nhập số tiền"
                  min="1"
                  required
                />
              </div>

              <div>
                <label className="label">Ngày</label>
                <input
                  type="date"
                  value={formData.transaction_date}
                  onChange={(e) =>
                    setFormData({ ...formData, transaction_date: e.target.value })
                  }
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="label">Mô tả (tùy chọn)</label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="input"
                  placeholder="Nhập mô tả"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={closeModal}
                  className="flex-1 btn btn-secondary"
                >
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
