import { useState, useEffect } from 'react';
import { summaryAPI, transactionsAPI } from '../services/api';
import {
  TrendingUp,
  TrendingDown,
  Wallet,
  PiggyBank,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

function formatCurrency(amount) {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(amount);
}

function StatCard({ title, value, icon: Icon, trend, trendValue, color }) {
  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-slate-900">{value}</p>
          {trend && (
            <p
              className={`text-sm mt-2 flex items-center gap-1 ${
                trend === 'up' ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {trend === 'up' ? (
                <ArrowUpRight className="w-4 h-4" />
              ) : (
                <ArrowDownRight className="w-4 h-4" />
              )}
              {trendValue}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );
}

const MONTH_NAMES_VI = [
  'Th1', 'Th2', 'Th3', 'Th4', 'Th5', 'Th6',
  'Th7', 'Th8', 'Th9', 'Th10', 'Th11', 'Th12'
];

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [monthlyData, setMonthlyData] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [summaryRes, monthlyRes, categoryRes, transactionsRes] =
        await Promise.all([
          summaryAPI.getDashboard(),
          summaryAPI.getMonthly(6),
          summaryAPI.getCategories('expense'),
          transactionsAPI.getAll({ limit: 5 }),
        ]);

      setSummary(summaryRes.data);
      setMonthlyData(monthlyRes.data.reverse());
      setCategoryData(categoryRes.data);
      setRecentTransactions(transactionsRes.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6'];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Tổng quan</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Tổng số dư"
          value={formatCurrency(summary?.total_balance || 0)}
          icon={Wallet}
          color="bg-primary-500"
        />
        <StatCard
          title="Thu nhập tháng này"
          value={formatCurrency(summary?.total_income_this_month || 0)}
          icon={TrendingUp}
          color="bg-green-500"
        />
        <StatCard
          title="Chi tiêu tháng này"
          value={formatCurrency(summary?.total_expense_this_month || 0)}
          icon={TrendingDown}
          color="bg-red-500"
        />
        <StatCard
          title="Tiết kiệm"
          value={formatCurrency(summary?.net_savings_this_month || 0)}
          icon={PiggyBank}
          trend={summary?.net_savings_this_month >= 0 ? 'up' : 'down'}
          trendValue={`${summary?.expense_ratio || 0}% tỷ lệ chi tiêu`}
          color="bg-accent-500"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Trend */}
        <div className="card">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">
            Thu nhập & Chi tiêu (6 tháng)
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis
                  dataKey="month"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(m) => MONTH_NAMES_VI[m - 1]}
                />
                <YAxis
                  tick={{ fontSize: 12 }}
                  tickFormatter={(v) => `${(v / 1000000).toFixed(0)}M`}
                />
                <Tooltip
                  formatter={(value) => formatCurrency(value)}
                  labelFormatter={(m) => `Tháng ${m}`}
                />
                <Bar dataKey="total_income" name="Thu nhập" fill="#22c55e" radius={[4, 4, 0, 0]} />
                <Bar dataKey="total_expense" name="Chi tiêu" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Expense by Category */}
        <div className="card">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">
            Chi tiêu theo danh mục
          </h2>
          <div className="h-64 flex items-center">
            {categoryData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    dataKey="total_amount"
                    nameKey="category_name"
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                  >
                    {categoryData.map((entry, index) => (
                      <Cell
                        key={entry.category_id}
                        fill={entry.category_color || COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => formatCurrency(value)} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-slate-500 text-center w-full">
                Chưa có dữ liệu chi tiêu tháng này
              </p>
            )}
            <div className="space-y-2 ml-4">
              {categoryData.slice(0, 5).map((cat, index) => (
                <div key={cat.category_id} className="flex items-center gap-2 text-sm">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{
                      backgroundColor: cat.category_color || COLORS[index % COLORS.length],
                    }}
                  />
                  <span className="text-slate-600">{cat.category_name}</span>
                  <span className="text-slate-400">({cat.percentage}%)</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="card">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">
          Giao dịch gần đây
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">
                  Ngày
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">
                  Danh mục
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-600">
                  Mô tả
                </th>
                <th className="text-right py-3 px-4 text-sm font-medium text-slate-600">
                  Số tiền
                </th>
              </tr>
            </thead>
            <tbody>
              {recentTransactions.map((tx) => (
                <tr key={tx.id} className="border-b border-slate-100 hover:bg-slate-50">
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
                  <td className="py-3 px-4 text-sm text-slate-600">
                    {tx.description || '-'}
                  </td>
                  <td
                    className={`py-3 px-4 text-sm font-medium text-right ${
                      tx.type === 'income' ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {tx.type === 'income' ? '+' : '-'}
                    {formatCurrency(tx.amount)}
                  </td>
                </tr>
              ))}
              {recentTransactions.length === 0 && (
                <tr>
                  <td colSpan={4} className="py-8 text-center text-slate-500">
                    Chưa có giao dịch nào
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
