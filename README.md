# 💰 Personal Finance BI System

A Personal Finance Intelligent Management System with Business Intelligence capabilities, built as an academic project for a Business Intelligence course.

## 🎯 Features

- **User Authentication**: Register, login, JWT-based authentication
- **Transaction Management**: Track income and expenses
- **Wallet Management**: Multiple wallets with automatic balance updates
- **Budget Tracking**: Set monthly budgets per category with alerts
- **Categories**: Default and custom categories for transactions
- **Dashboard**: Visual overview with charts and KPIs
- **BI Dashboards**: Apache Superset integration for advanced analytics
- **Automation**: n8n workflows for alerts and reminders
- **AI Chatbot**: Dify integration for natural language queries (Phase 4)

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | FastAPI (Python) + SQLAlchemy |
| Database | PostgreSQL 15 |
| BI | Apache Superset |
| Automation | n8n |
| AI Chatbot | Dify |
| DevOps | Docker Compose |

## 📋 Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine + Docker Compose (Linux)
- Git
- 8GB+ RAM recommended

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd personal-finance-bi
```

### 2. Create environment file

```bash
# Copy the example env file
cp env.example .env

# Edit .env if needed (default values work for development)
```

### 3. Start all services

```bash
docker-compose up --build
```

Wait for all services to start (first run may take 5-10 minutes to download images).

### 4. Access the application

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Register or use demo account |
| **Backend API** | http://localhost:8000/docs | - |
| **Superset** | http://localhost:8088 | admin / admin |
| **n8n** | http://localhost:5678 | admin / admin |
| **Mailhog** | http://localhost:8025 | - |

### 5. Demo Account

```
Email: demo@finance.app
Password: 123456
```

## 📁 Project Structure

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
│       └── utils/             # Utilities (auth, etc.)
│
├── frontend/                   # React frontend
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── main.jsx           # Entry point
│       ├── App.jsx            # Routes
│       ├── components/        # Reusable components
│       ├── pages/             # Page components
│       ├── services/          # API services
│       └── context/           # React contexts
│
└── database/                   # Database scripts
    ├── init.sql               # Schema + views
    └── seed.sql               # Demo data
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user

### Wallets
- `GET /api/wallets` - List wallets
- `POST /api/wallets` - Create wallet
- `PUT /api/wallets/{id}` - Update wallet
- `DELETE /api/wallets/{id}` - Delete wallet

### Categories
- `GET /api/categories` - List categories
- `POST /api/categories` - Create category
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category

### Transactions
- `GET /api/transactions` - List transactions (with filters)
- `POST /api/transactions` - Create transaction
- `PUT /api/transactions/{id}` - Update transaction
- `DELETE /api/transactions/{id}` - Delete transaction

### Budgets
- `GET /api/budgets` - List budgets
- `GET /api/budgets/status` - Get budget status with spending
- `POST /api/budgets` - Create budget
- `PUT /api/budgets/{id}` - Update budget
- `DELETE /api/budgets/{id}` - Delete budget

### Summary
- `GET /api/summary/dashboard` - Dashboard summary
- `GET /api/summary/monthly` - Monthly trends
- `GET /api/summary/categories` - Category breakdown

## 🗄️ Database Schema

### Tables
- `users` - User accounts
- `wallets` - Money accounts
- `categories` - Transaction categories
- `transactions` - Income/expense records
- `budgets` - Monthly budget limits

### Analytical Views (for BI)
- `v_daily_summary` - Daily aggregations
- `v_monthly_summary` - Monthly aggregations
- `v_category_breakdown` - Spending by category
- `v_income_vs_expense` - Income vs expense comparison
- `v_budget_vs_actual` - Budget monitoring
- `v_wallet_balance` - Wallet summaries
- `v_recent_transactions` - Recent transactions with details

## 🔧 Development

### Running locally without Docker

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

### Stopping services

```bash
docker-compose down
```

### Reset database

```bash
docker-compose down -v  # Removes volumes
docker-compose up --build
```

## 📊 Phase 2: Superset Setup

1. Access Superset at http://localhost:8088
2. Login with admin / admin
3. Add Database connection:
   - Database: PostgreSQL
   - Host: postgres
   - Port: 5432
   - Database: finance_db
   - User: superset_readonly
   - Password: superset_pass
4. Create datasets from the `v_*` views
5. Build charts and dashboards

## ⚡ Phase 3: n8n Setup

1. Access n8n at http://localhost:5678
2. Login with admin / admin
3. Create workflows for:
   - Monthly bill reminders
   - Budget overrun alerts
   - Large expense notifications
4. Configure SMTP (use Mailhog for testing)

## 🤖 Phase 4: Dify Setup

See Phase 4 documentation for Dify chatbot integration.

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

Built with ❤️ for Business Intelligence Course
