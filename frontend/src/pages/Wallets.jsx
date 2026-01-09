import { useState, useEffect } from 'react';
import { walletsAPI } from '../services/api';
import { Plus, Edit, Trash2, X, Loader2, Wallet, CreditCard, Smartphone, Building } from 'lucide-react';

function formatCurrency(amount) {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(amount);
}

const WALLET_ICONS = [
  { id: 'wallet', icon: Wallet, label: 'Ví tiền' },
  { id: 'credit-card', icon: CreditCard, label: 'Thẻ' },
  { id: 'smartphone', icon: Smartphone, label: 'Ví điện tử' },
  { id: 'building', icon: Building, label: 'Ngân hàng' },
];

export default function Wallets() {
  const [wallets, setWallets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingWallet, setEditingWallet] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    initial_balance: '',
    currency: 'VND',
    icon: 'wallet',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchWallets();
  }, []);

  const fetchWallets = async () => {
    try {
      const response = await walletsAPI.getAll();
      setWallets(response.data);
    } catch (error) {
      console.error('Failed to fetch wallets:', error);
    } finally {
      setLoading(false);
    }
  };

  const openModal = (wallet = null) => {
    if (wallet) {
      setEditingWallet(wallet);
      setFormData({
        name: wallet.name,
        initial_balance: '',
        currency: wallet.currency,
        icon: wallet.icon,
      });
    } else {
      setEditingWallet(null);
      setFormData({
        name: '',
        initial_balance: '',
        currency: 'VND',
        icon: 'wallet',
      });
    }
    setError('');
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingWallet(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      if (editingWallet) {
        await walletsAPI.update(editingWallet.id, {
          name: formData.name,
          icon: formData.icon,
        });
      } else {
        await walletsAPI.create({
          name: formData.name,
          initial_balance: parseFloat(formData.initial_balance) || 0,
          currency: formData.currency,
          icon: formData.icon,
        });
      }

      closeModal();
      fetchWallets();
    } catch (err) {
      setError(err.response?.data?.detail || 'Không thể lưu ví');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Bạn có chắc chắn muốn xóa ví này?')) return;

    try {
      await walletsAPI.delete(id);
      fetchWallets();
    } catch (error) {
      console.error('Failed to delete:', error);
      alert('Không thể xóa ví có giao dịch');
    }
  };

  const totalBalance = wallets.reduce((sum, w) => sum + parseFloat(w.balance), 0);

  const getIcon = (iconId) => {
    const found = WALLET_ICONS.find((i) => i.id === iconId);
    return found?.icon || Wallet;
  };

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
        <h1 className="text-2xl font-bold text-slate-900">Ví tiền</h1>
        <button onClick={() => openModal()} className="btn btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Thêm ví
        </button>
      </div>

      {/* Total Balance Card */}
      <div className="card bg-gradient-to-r from-primary-500 to-primary-600 text-white">
        <p className="text-primary-100 text-sm mb-1">Tổng số dư</p>
        <p className="text-3xl font-bold">{formatCurrency(totalBalance)}</p>
      </div>

      {/* Wallets Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {wallets.map((wallet) => {
          const IconComponent = getIcon(wallet.icon);
          return (
            <div key={wallet.id} className="card">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-lg bg-primary-100">
                    <IconComponent className="w-6 h-6 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">{wallet.name}</h3>
                    <p className="text-sm text-slate-500">{wallet.currency}</p>
                  </div>
                </div>
                <div className="flex gap-1">
                  <button
                    onClick={() => openModal(wallet)}
                    className="p-1 text-slate-400 hover:text-primary-600 transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(wallet.id)}
                    className="p-1 text-slate-400 hover:text-red-600 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <p className="text-2xl font-bold text-slate-900 mt-4">
                {formatCurrency(wallet.balance)}
              </p>
            </div>
          );
        })}

        {wallets.length === 0 && (
          <div className="col-span-full text-center py-12 text-slate-500">
            Chưa có ví nào. Nhấn "Thêm ví" để tạo mới.
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
            <div className="flex items-center justify-between p-4 border-b border-slate-200">
              <h2 className="text-lg font-semibold">
                {editingWallet ? 'Sửa ví' : 'Thêm ví'}
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
                <label className="label">Tên ví</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="input"
                  placeholder="VD: Tiền mặt, Tài khoản ngân hàng"
                  required
                />
              </div>

              {!editingWallet && (
                <div>
                  <label className="label">Số dư ban đầu (VND)</label>
                  <input
                    type="number"
                    value={formData.initial_balance}
                    onChange={(e) =>
                      setFormData({ ...formData, initial_balance: e.target.value })
                    }
                    className="input"
                    placeholder="0"
                    min="0"
                  />
                </div>
              )}

              <div>
                <label className="label">Biểu tượng</label>
                <div className="flex gap-2">
                  {WALLET_ICONS.map(({ id, icon: Icon, label }) => (
                    <button
                      key={id}
                      type="button"
                      onClick={() => setFormData({ ...formData, icon: id })}
                      className={`p-3 rounded-lg border-2 transition-colors ${
                        formData.icon === id
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-slate-200 hover:border-slate-300'
                      }`}
                      title={label}
                    >
                      <Icon className="w-5 h-5" />
                    </button>
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
