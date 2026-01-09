# 💰 Hệ thống Quản lý Tài chính Cá nhân Thông minh
# Personal Finance BI System

Hệ thống Quản lý Tài chính Cá nhân Thông minh tích hợp Business Intelligence, được xây dựng như một dự án học thuật cho môn học Hệ thống Kinh doanh Thông minh.

A Personal Finance Intelligent Management System with Business Intelligence capabilities, built as an academic project for a Business Intelligence course.

## 🎯 Tính năng / Features

- **Xác thực người dùng**: Đăng ký, đăng nhập, xác thực JWT
- **Quản lý giao dịch**: Theo dõi thu nhập và chi tiêu
- **Quản lý ví**: Nhiều ví với cập nhật số dư tự động
- **Theo dõi ngân sách**: Đặt ngân sách hàng tháng theo danh mục với cảnh báo
- **Danh mục**: Danh mục mặc định và tùy chỉnh cho giao dịch
- **Dashboard**: Tổng quan trực quan với biểu đồ và KPI
- **BI Dashboards**: Tích hợp Apache Superset cho phân tích nâng cao
- **Tự động hóa**: n8n workflows cho cảnh báo và nhắc nhở
- **AI Chatbot**: Tích hợp Dify cho truy vấn bằng ngôn ngữ tự nhiên

## 🛠️ Công nghệ / Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | FastAPI (Python) + SQLAlchemy |
| Database | PostgreSQL 15 |
| BI | Apache Superset |
| Automation | n8n |
| AI Chatbot | Dify Cloud |
| DevOps | Docker Compose |

## 📋 Yêu cầu / Prerequisites

- Docker Desktop (Windows/Mac) hoặc Docker Engine + Docker Compose (Linux)
- Git
- 8GB+ RAM khuyến nghị
- (Tùy chọn) ngrok account để tích hợp Dify AI

## 🚀 Hướng dẫn Chạy / Quick Start

### 1. Clone repository

```bash
git clone https://github.com/ThuanDanch);/personal-finance-bi.git
cd personal-finance-bi
```

### 2. Tạo file môi trường / Create environment file

```bash
# Copy file env mẫu
cp env.example .env
```

**Nội dung file `.env`:**
```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_DB=finance_db

# Backend
DATABASE_URL=postgresql://postgres:postgres123@postgres:5432/finance_db
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Service Keys (cho n8n và Dify)
N8N_SERVICE_KEY=n8n-service-key
DIFY_SERVICE_KEY=dify-service-key
GUEST_TOKEN_SECRET=guest-secret-key-change-this
```

### 3. Khởi động tất cả services / Start all services

```bash
docker-compose up --build
```

Đợi tất cả services khởi động (lần đầu có thể mất 5-10 phút để tải images).

### 4. Truy cập ứng dụng / Access the application

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Đăng ký hoặc dùng tài khoản demo |
| **Backend API** | http://localhost:8000/docs | - |
| **Superset** | http://localhost:8088 | admin / admin |
| **n8n** | http://localhost:5678 | admin / admin |
| **Mailhog** | http://localhost:8025 | - |

### 5. Tài khoản Demo / Demo Account

```
Email: demo@finance.app
Password: 123456
```

## 🖥️ Giao diện / Screenshots

### Dashboard
- Tổng quan thu chi
- Biểu đồ xu hướng
- Thống kê theo danh mục

### AI Chatbot
- Hỏi đáp bằng tiếng Việt
- Tích hợp Dify AI
- Gợi ý câu hỏi thông minh

## 📁 Cấu trúc dự án / Project Structure

```
personal-finance-bi/
├── docker-compose.yml          # Docker orchestration
├── .env                        # Environment variables
├── README.md                   # This file
│
├── backend/                    # FastAPI backend
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py            # Application entry point
│       ├── config.py          # Settings
│       ├── database.py        # DB connection
│       ├── models/            # SQLAlchemy models
│       ├── schemas/           # Pydantic schemas
│       ├── routers/           # API endpoints
│       │   ├── auth.py        # Authentication
│       │   ├── wallets.py     # Wallet management
│       │   ├── categories.py  # Categories
│       │   ├── transactions.py# Transactions
│       │   ├── budgets.py     # Budgets
│       │   ├── summary.py     # Dashboard summary
│       │   ├── automation.py  # n8n automation
│       │   └── chatbot.py     # Dify chatbot API
│       ├── services/          # Business logic
│       │   └── chatbot_service.py  # Chatbot service
│       └── utils/             # Utilities (auth, etc.)
│
├── frontend/                   # React frontend (Vietnamese UI)
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── main.jsx           # Entry point
│       ├── App.jsx            # Routes
│       ├── components/        # Reusable components
│       │   ├── Layout.jsx     # Main layout
│       │   └── Chatbot.jsx    # AI Chatbot component
│       ├── pages/             # Page components (Vietnamese)
│       │   ├── Dashboard.jsx  # Tổng quan
│       │   ├── Transactions.jsx # Giao dịch
│       │   ├── Wallets.jsx    # Ví tiền
│       │   ├── Budgets.jsx    # Ngân sách
│       │   ├── Categories.jsx # Danh mục
│       │   ├── Login.jsx      # Đăng nhập
│       │   └── Register.jsx   # Đăng ký
│       ├── services/          # API services
│       │   └── api.js         # Backend + Dify API
│       └── context/           # React contexts
│
├── database/                   # Database scripts
│   ├── init.sql               # Schema + basic views
│   ├── seed.sql               # Demo data
│   ├── bi_views.sql           # Advanced BI views
│   └── 04-bills.sql           # Bills table for automation
│
├── superset/                   # Superset configuration
│   ├── Dockerfile
│   ├── superset_config.py
│   └── dashboards/
│
└── n8n/                        # n8n automation
    └── workflows/
        ├── monthly_bill_reminder.json
        └── budget_overrun_alert.json
```

## 🤖 Tích hợp AI Chatbot (Dify)

### Kiến trúc / Architecture

```
┌─────────────────┐                ┌─────────────────┐
│   Frontend      │ ──────────────►│   Dify Cloud    │
│   (React)       │   Dify API     │   (AI Model)    │
└─────────────────┘                └────────┬────────┘
                                           │
                                           │ HTTP Tool
                                           ▼
┌─────────────────┐                ┌─────────────────┐
│   PostgreSQL    │ ◄──────────────│   Backend       │
│   (Database)    │                │   (FastAPI)     │
└─────────────────┘                └─────────────────┘
```

### Cách hoạt động / How it works

1. **Frontend** gửi câu hỏi tiếng Việt đến **Dify Cloud** API
2. **Dify AI** (Gemini/GPT) xử lý và gọi **HTTP Tool** đến Backend
3. **Backend** query database và trả về dữ liệu
4. **Dify AI** format câu trả lời và gửi về Frontend

### Thiết lập Dify Cloud / Setup Dify Cloud

#### Bước 1: Tạo tài khoản Dify

1. Truy cập https://cloud.dify.ai
2. Đăng ký tài khoản miễn phí
3. Tạo Workspace mới

#### Bước 2: Cấu hình Model

1. Vào **Settings** → **Model Provider**
2. Thêm API Key cho một trong các model sau:
   - **Gemini** (khuyến nghị, miễn phí): https://aistudio.google.com/app/apikey
   - **Groq** (miễn phí, nhanh): https://console.groq.com/keys
   - **OpenAI** (trả phí): https://platform.openai.com/api-keys

#### Bước 3: Tạo Chat App

1. Click **Create App** → **Create from Blank**
2. Chọn **Agent** 
3. Đặt tên: "Trợ lý Tài chính"

#### Bước 4: Cấu hình System Prompt

```
Bạn là trợ lý tài chính cá nhân thông minh. Bạn giúp người dùng:
- Xem tổng quan thu chi hàng tháng
- Phân tích chi tiêu theo danh mục
- Kiểm tra tình trạng ngân sách
- Xem số dư ví
- Tra cứu giao dịch gần đây

Quy tắc:
1. Luôn trả lời bằng tiếng Việt
2. Sử dụng emoji để làm câu trả lời sinh động hơn
3. Khi người dùng hỏi về tài chính, LUÔN gọi tool "queryFinance" với user_id = 1
4. Format số tiền theo VND (ví dụ: 1,500,000 VND)
5. Sau mỗi câu trả lời, đề xuất các câu hỏi tiếp theo
```

#### Bước 5: Thêm Custom Tool

1. Trong app, vào section **Tools** → **+ Add**
2. Chọn **Custom Tool**
3. Nhấn **Import from URL**
4. Nhập URL: `https://YOUR-NGROK-URL/chatbot/openapi.json`

**Hoặc paste schema thủ công:**

```yaml
openapi: 3.0.0
info:
  title: Finance Chatbot API
  version: 1.0.0
servers:
  - url: https://YOUR-NGROK-URL
paths:
  /chatbot/query:
    post:
      operationId: queryFinance
      summary: Query user finance data
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                user_id:
                  type: integer
                  description: User ID (use 1 for demo)
                question:
                  type: string
                  description: Question about finance in Vietnamese
                timezone:
                  type: string
                  default: Asia/Ho_Chi_Minh
              required:
                - user_id
                - question
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  answer:
                    type: string
                  data:
                    type: object
```

#### Bước 6: Expose Backend với ngrok

```bash
# Cài đặt ngrok
# Windows: choco install ngrok
# Mac: brew install ngrok

# Đăng nhập ngrok
ngrok config add-authtoken YOUR_AUTH_TOKEN

# Chạy tunnel
ngrok http 8000
```

Copy URL ngrok (vd: `https://abc123.ngrok-free.app`) và cập nhật vào Dify Tool settings.

#### Bước 7: Lấy API Key và cập nhật Frontend

1. Trong Dify, vào **API Access** (menu bên trái)
2. Copy **API Key** (bắt đầu bằng `app-`)
3. Cập nhật file `frontend/src/services/api.js`:

```javascript
const DIFY_CONFIG = {
  apiKey: 'app-YOUR-DIFY-API-KEY-HERE',
  apiUrl: 'https://api.dify.ai/v1',
};
```

4. Rebuild frontend:
```bash
docker-compose up -d --build frontend
```

### Câu hỏi Demo / Demo Questions

| # | Câu hỏi | Ý định |
|---|---------|--------|
| 1 | Tổng chi tiêu tháng này là bao nhiêu? | Tổng chi tiêu |
| 2 | Thu nhập tháng này của tôi? | Tổng thu nhập |
| 3 | Chi tiêu theo danh mục | Phân tích danh mục |
| 4 | Kiểm tra ngân sách tháng này | Tình trạng ngân sách |
| 5 | Số dư trong ví là bao nhiêu? | Số dư ví |
| 6 | Giao dịch gần đây | Lịch sử giao dịch |

## ⚡ Tự động hóa n8n / n8n Automation

### Workflows có sẵn / Pre-built Workflows

| Workflow | Trigger | Mô tả |
|----------|---------|-------|
| Monthly Bill Reminder | Ngày 1 hàng tháng | Nhắc thanh toán hóa đơn |
| Budget Overrun Alert | Hàng ngày 9AM | Cảnh báo vượt ngân sách |

### Thiết lập / Setup

1. Truy cập n8n: http://localhost:5678
2. Login: admin / admin
3. Import workflows từ `n8n/workflows/`
4. Tạo credentials:
   - **MailHog SMTP**: Host=mailhog, Port=1025
   - **PostgreSQL**: Host=postgres, Port=5432, DB=finance_db, User=n8n_readonly, Pass=n8n_pass

### Xem email test / View test emails

Truy cập MailHog UI: http://localhost:8025

## 📊 BI Dashboards (Superset)

### Truy cập / Access

- URL: http://localhost:8088
- Login: admin / admin

### Views có sẵn / Available Views

| View | Mô tả | Use Case |
|------|-------|----------|
| `v_kpi_summary` | Dashboard KPIs | Summary cards |
| `v_monthly_cashflow` | Xu hướng hàng tháng | Trend analysis |
| `v_category_breakdown` | Chi tiêu theo danh mục | Pie charts |
| `v_budget_vs_actual` | So sánh ngân sách | Progress bars |
| `v_savings_rate` | Tỷ lệ tiết kiệm | Gauge charts |

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Đăng ký
- `POST /api/auth/login` - Đăng nhập
- `GET /api/auth/me` - Thông tin user

### Wallets
- `GET /api/wallets` - Danh sách ví
- `POST /api/wallets` - Tạo ví
- `PUT /api/wallets/{id}` - Cập nhật ví
- `DELETE /api/wallets/{id}` - Xóa ví

### Categories
- `GET /api/categories` - Danh sách danh mục
- `POST /api/categories` - Tạo danh mục

### Transactions
- `GET /api/transactions` - Danh sách giao dịch
- `POST /api/transactions` - Tạo giao dịch

### Budgets
- `GET /api/budgets` - Danh sách ngân sách
- `GET /api/budgets/status` - Tình trạng ngân sách

### Chatbot
- `GET /chatbot/health` - Health check
- `POST /chatbot/query` - Query tài chính
- `GET /chatbot/views` - Danh sách views

### Automation
- `GET /api/automation/bills/upcoming` - Hóa đơn sắp tới
- `GET /api/automation/budget/overruns` - Vượt ngân sách

## 🛠️ Development

### Chạy local không Docker / Run locally without Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Dừng services / Stop services

```bash
docker-compose down
```

### Reset database / Reset database

```bash
docker-compose down -v  # Xóa volumes
docker-compose up --build
```

## 🐛 Troubleshooting

| Vấn đề | Giải pháp |
|--------|-----------|
| Frontend không load | Kiểm tra `docker-compose logs frontend` |
| Chatbot lỗi "blocking mode" | Đảm bảo dùng streaming mode (đã fix) |
| n8n không có dữ liệu | Chạy `database/04-bills.sql` |
| Dify tool không hoạt động | Kiểm tra ngrok URL còn active |
| Rate limit Gemini | Đợi 1 phút hoặc đổi sang Groq |

## 📝 Changelog

### Phase 5 - AI Chatbot Integration
- ✅ Tích hợp Dify Cloud API
- ✅ Chatbot UI trong frontend
- ✅ Streaming mode cho Agent apps
- ✅ Giao diện tiếng Việt hoàn chỉnh

### Phase 4 - Automation
- ✅ n8n workflows
- ✅ Bill reminder
- ✅ Budget overrun alerts

### Phase 3 - BI Dashboards
- ✅ Superset integration
- ✅ Advanced BI views
- ✅ Pre-built dashboards

### Phase 2 - Core Features
- ✅ Transaction management
- ✅ Wallet & Budget
- ✅ Dashboard

### Phase 1 - Foundation
- ✅ Authentication
- ✅ Database schema
- ✅ Docker setup

## 👥 Team

| Role | Responsibilities |
|------|------------------|
| Frontend Developer | React UI, Pages, Components |
| Backend Developer | FastAPI, APIs, Authentication |
| BI/Data Developer | Database, Superset, Docker |
| AI/Automation Developer | n8n, Dify, Testing |

## 📝 License

This project is for educational purposes only.

---

Built with ❤️ for Business Intelligence Course - Thủy Lợi University
