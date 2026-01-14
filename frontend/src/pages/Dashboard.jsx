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
  Legend,
} from 'recharts';

function formatCurrency(amount) {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(amount);
}

// function StatCard({ title, value, icon: Icon, trend, trendValue, color }) {
//   return (
//     <div className="card">
//       <div className="flex items-start justify-between">
//         <div>
//           <p className="text-sm text-slate-600 mb-1">{title}</p>
//           <p className="text-2xl font-bold text-slate-900">{value}</p>
//           {trend && (
//             <p
//               className={`text-sm mt-2 flex items-center gap-1 ${
//                 trend === 'up' ? 'text-green-600' : 'text-red-600'
//               }`}
//             >
//               {trend === 'up' ? (
//                 <ArrowUpRight className="w-4 h-4" />
//               ) : (
//                 <ArrowDownRight className="w-4 h-4" />
//               )}
//               {trendValue}
//             </p>
//           )}
//         </div>
//         <div className={`p-3 rounded-lg ${color}`}>
//           <Icon className="w-6 h-6 text-white" />
//         </div>
//       </div>
//     </div>
//   );
// }
function StatCard({ title, value, icon: Icon, trend, trendValue, color }) {
  return (
    <div className="card">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <p className="text-sm text-slate-500 font-medium mb-1">{title}</p>
          <p className="text-xl font-bold text-slate-900">{value}</p>
          {trend && (
            <p
              className={`text-sm mt-2 flex items-center gap-1 font-medium ${
                trend === 'up' ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {trend === 'up' ? (
                <ArrowUpRight className="w-4 h-4 flex-shrink-0" />
              ) : (
                <ArrowDownRight className="w-4 h-4 flex-shrink-0" />
              )}
              <span className="whitespace-nowrap">{trendValue}</span>
            </p>
          )}
        </div>
        <div className={`w-11 h-11 rounded-xl ${color} flex items-center justify-center shadow-sm flex-shrink-0`}>
          <Icon className="w-5 h-5 text-white" />
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

  // --- XỬ LÝ DỮ LIỆU ---
  
  // 1. Ép kiểu cho Biểu đồ tròn
  const pieChartData = categoryData.map(item => ({
    ...item,
    total_amount: Number(item.total_amount)
  }));

  // 2. Ép kiểu cho Biểu đồ cột
  const formattedMonthlyData = monthlyData.map(item => ({
    ...item,
    total_income: Number(item.total_income),
    total_expense: Number(item.total_expense)
  }));

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

      {/* Stats Grid - Sử dụng StatCard mới */}
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
              <BarChart
                data={formattedMonthlyData} // <--- Dùng dữ liệu đã ép kiểu số
                margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                barGap={8}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis
                  dataKey="month"
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  tickFormatter={(m) => MONTH_NAMES_VI[m - 1]}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  tickFormatter={(v) => `${(v / 1000000).toFixed(0)}M`}
                  axisLine={false}
                  tickLine={false}
                  width={40}
                />
                <Tooltip
                  cursor={{ fill: '#f1f5f9' }}
                  formatter={(value) => formatCurrency(value)}
                  labelFormatter={(m) => `Tháng ${m}`}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Legend iconType="circle" wrapperStyle={{ paddingTop: '10px' }} />
                
                <Bar 
                  dataKey="total_income" 
                  name="Thu nhập" 
                  fill="#22c55e" 
                  radius={[4, 4, 0, 0]} 
                  barSize={12} // Giảm kích thước cột một chút cho thanh thoát
                />
                <Bar 
                  dataKey="total_expense" 
                  name="Chi tiêu" 
                  fill="#ef4444" 
                  radius={[4, 4, 0, 0]} 
                  barSize={12} 
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Expense by Category */}
        <div className="card">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">
            Chi tiêu theo danh mục
          </h2>
          <div className="h-64">
            {pieChartData.length > 0 ? (
              <div className="flex items-center h-full">
                {/* Biểu đồ tròn - bên trái */}
                <div className="flex-1 h-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieChartData}
                        dataKey="total_amount"
                        nameKey="category_name"
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={90}
                        paddingAngle={3}
                      >
                        {pieChartData.map((entry, index) => (
                          <Cell
                            key={entry.category_id}
                            fill={entry.category_color || COLORS[index % COLORS.length]}
                            strokeWidth={0}
                          />
                        ))}
                      </Pie>
                      <Tooltip 
                        formatter={(value) => formatCurrency(value)} 
                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                
                {/* Chú thích - bên phải */}
                <div className="w-48 space-y-3 pl-4">
                  {pieChartData.slice(0, 5).map((cat, index) => (
                    <div key={cat.category_id} className="flex items-start gap-2.5">
                      <div
                        className="w-3 h-3 rounded-full flex-shrink-0 mt-1"
                        style={{
                          backgroundColor: cat.category_color || COLORS[index % COLORS.length],
                        }}
                      />
                      <div>
                        <p className="text-sm font-semibold text-slate-800">
                          {cat.category_name}
                        </p>
                        <p className="text-sm text-slate-500">
                          {cat.percentage}% ({formatCurrency(cat.total_amount)})
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-500 bg-slate-50 rounded-lg">
                <p>Chưa có dữ liệu chi tiêu</p>
              </div>
            )}
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
