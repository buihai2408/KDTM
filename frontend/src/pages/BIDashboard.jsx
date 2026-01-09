import { useState, useEffect } from 'react';
import { BarChart3, ExternalLink, RefreshCw, Maximize2, Settings } from 'lucide-react';

// Superset Dashboard URLs
const SUPERSET_BASE_URL = 'http://localhost:8088';

const DASHBOARDS = [
  {
    id: 1,
    name: 'Tổng quan Tài chính',
    description: 'Dashboard tổng quan với KPIs, xu hướng thu chi, phân tích danh mục',
    path: '/superset/dashboard/1/',
    embedPath: '/superset/dashboard/1/?standalone=1&show_filters=0',
  },
  {
    id: 2,
    name: 'Phân tích Chi tiêu',
    description: 'Chi tiết chi tiêu theo danh mục, thời gian, xu hướng',
    path: '/superset/dashboard/2/',
    embedPath: '/superset/dashboard/2/?standalone=1&show_filters=0',
  },
  {
    id: 3,
    name: 'Ngân sách & Tiết kiệm',
    description: 'Theo dõi ngân sách, tỷ lệ tiết kiệm, mục tiêu tài chính',
    path: '/superset/dashboard/3/',
    embedPath: '/superset/dashboard/3/?standalone=1&show_filters=0',
  },
];

export default function BIDashboard() {
  const [selectedDashboard, setSelectedDashboard] = useState(DASHBOARDS[0]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showInstructions, setShowInstructions] = useState(false);

  const handleIframeLoad = () => {
    setIsLoading(false);
  };

  const refreshDashboard = () => {
    setIsLoading(true);
    // Force iframe refresh
    const iframe = document.getElementById('superset-iframe');
    if (iframe) {
      iframe.src = iframe.src;
    }
  };

  const openInNewTab = () => {
    window.open(`${SUPERSET_BASE_URL}${selectedDashboard.path}`, '_blank');
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  return (
    <div className={`${isFullscreen ? 'fixed inset-0 z-50 bg-white' : ''}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6 p-4 bg-white rounded-xl shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-100 rounded-lg">
            <BarChart3 className="w-6 h-6 text-indigo-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800">BI Dashboards</h1>
            <p className="text-slate-500 text-sm">Phân tích dữ liệu với Apache Superset</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowInstructions(!showInstructions)}
            className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            title="Hướng dẫn"
          >
            <Settings className="w-5 h-5" />
          </button>
          <button
            onClick={refreshDashboard}
            className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            title="Làm mới"
          >
            <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={toggleFullscreen}
            className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            title="Toàn màn hình"
          >
            <Maximize2 className="w-5 h-5" />
          </button>
          <button
            onClick={openInNewTab}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
            Mở Superset
          </button>
        </div>
      </div>

      {/* Instructions Panel */}
      {showInstructions && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-xl">
          <h3 className="font-semibold text-blue-800 mb-2">📊 Hướng dẫn tạo Dashboard trong Superset</h3>
          <ol className="text-sm text-blue-700 space-y-2 list-decimal list-inside">
            <li>Truy cập <a href={SUPERSET_BASE_URL} target="_blank" rel="noopener noreferrer" className="underline font-medium">Superset ({SUPERSET_BASE_URL})</a></li>
            <li>Đăng nhập với <strong>admin / admin</strong></li>
            <li>Vào <strong>Settings → Database Connections → + Database</strong></li>
            <li>Thêm PostgreSQL: Host=<code>postgres</code>, Port=<code>5432</code>, DB=<code>finance_db</code>, User=<code>superset_readonly</code>, Pass=<code>superset_pass</code></li>
            <li>Vào <strong>Data → Datasets → + Dataset</strong>, chọn các views <code>v_*</code></li>
            <li>Tạo Charts từ datasets</li>
            <li>Tạo Dashboard và thêm charts vào</li>
            <li>Ghi nhớ Dashboard ID (số trong URL) để cập nhật ở đây</li>
          </ol>
        </div>
      )}

      {/* Dashboard Tabs */}
      <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
        {DASHBOARDS.map((dashboard) => (
          <button
            key={dashboard.id}
            onClick={() => {
              setSelectedDashboard(dashboard);
              setIsLoading(true);
            }}
            className={`flex-shrink-0 px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedDashboard.id === dashboard.id
                ? 'bg-indigo-500 text-white'
                : 'bg-white text-slate-600 hover:bg-slate-100'
            }`}
          >
            {dashboard.name}
          </button>
        ))}
      </div>

      {/* Dashboard Info */}
      <div className="mb-4 p-3 bg-slate-100 rounded-lg">
        <p className="text-sm text-slate-600">
          <strong>{selectedDashboard.name}:</strong> {selectedDashboard.description}
        </p>
      </div>

      {/* Superset Iframe */}
      <div className={`relative bg-white rounded-xl shadow-sm overflow-hidden ${isFullscreen ? 'h-[calc(100vh-200px)]' : 'h-[600px]'}`}>
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-50 z-10">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin mx-auto mb-3" />
              <p className="text-slate-600">Đang tải dashboard...</p>
              <p className="text-sm text-slate-400 mt-1">Nếu không hiển thị, hãy đăng nhập Superset trước</p>
            </div>
          </div>
        )}
        
        <iframe
          id="superset-iframe"
          src={`${SUPERSET_BASE_URL}${selectedDashboard.embedPath}`}
          className="w-full h-full border-0"
          onLoad={handleIframeLoad}
          title={selectedDashboard.name}
          sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
        />
      </div>

      {/* Quick Links */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <a
          href={`${SUPERSET_BASE_URL}/chart/list/`}
          target="_blank"
          rel="noopener noreferrer"
          className="p-4 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow"
        >
          <h3 className="font-semibold text-slate-800 mb-1">📈 Quản lý Charts</h3>
          <p className="text-sm text-slate-500">Xem và chỉnh sửa tất cả charts</p>
        </a>
        
        <a
          href={`${SUPERSET_BASE_URL}/dashboard/list/`}
          target="_blank"
          rel="noopener noreferrer"
          className="p-4 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow"
        >
          <h3 className="font-semibold text-slate-800 mb-1">📊 Quản lý Dashboards</h3>
          <p className="text-sm text-slate-500">Xem và chỉnh sửa tất cả dashboards</p>
        </a>
        
        <a
          href={`${SUPERSET_BASE_URL}/sqllab/`}
          target="_blank"
          rel="noopener noreferrer"
          className="p-4 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow"
        >
          <h3 className="font-semibold text-slate-800 mb-1">💻 SQL Lab</h3>
          <p className="text-sm text-slate-500">Viết SQL queries trực tiếp</p>
        </a>
      </div>
    </div>
  );
}
