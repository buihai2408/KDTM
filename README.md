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
├── database/                   # Database scripts
│   ├── init.sql               # Schema + basic views
│   ├── seed.sql               # Demo data
│   └── bi_views.sql           # Advanced BI views (Phase 3)
│
├── superset/                   # Superset configuration
│   ├── Dockerfile             # Custom Superset image
│   ├── Dockerfile.bootstrap   # Bootstrap container
│   ├── superset_config.py     # Superset configuration
│   ├── bootstrap_superset.py  # Auto-setup script
│   └── dashboards/            # Dashboard JSON templates
│       └── finance_dashboard.json
│
├── scripts/                    # Utility scripts
│   ├── init-superset.ps1      # Windows setup script
│   └── init-superset.sh       # Linux/Mac setup script
│
└── n8n/                        # n8n automation (Phase 4)
    ├── README.md              # Workflow documentation
    └── workflows/
        ├── monthly_bill_reminder.json
        └── budget_overrun_alert.json
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

### Automation (Phase 4)
- `GET /api/automation/bills/upcoming` - Get upcoming bills for a month
- `GET /api/automation/budget/overruns` - Get budget overruns
- `GET /api/automation/health` - Automation service health check

## 🗄️ Database Schema

### Tables
- `users` - User accounts
- `wallets` - Money accounts
- `categories` - Transaction categories
- `transactions` - Income/expense records
- `budgets` - Monthly budget limits
- `bills` - Recurring bills tracking (Phase 4)
- `dim_date` - Date dimension table for BI analysis

### Analytical Views (for BI)

**Basic Views:**
- `v_daily_summary` - Daily aggregations
- `v_monthly_summary` - Monthly aggregations
- `v_category_breakdown` - Spending by category
- `v_income_vs_expense` - Income vs expense comparison
- `v_budget_vs_actual` - Budget monitoring
- `v_wallet_balance` - Wallet summaries
- `v_recent_transactions` - Recent transactions with details

**Advanced BI Views (Phase 3):**
- `v_fact_transactions` - Enriched transaction fact table
- `v_weekly_trends` - Weekly spending trends
- `v_spending_by_day_of_week` - Day-of-week spending patterns
- `v_spending_by_hour` - Hour-of-day spending patterns
- `v_monthly_cashflow` - Monthly cashflow with MoM changes
- `v_category_growth` - Category spending growth analysis
- `v_top_categories` - Ranked spending categories
- `v_budget_performance` - Enhanced budget performance metrics
- `v_savings_rate` - Savings rate analysis
- `v_wallet_analytics` - Wallet activity analytics
- `v_user_financial_health` - User financial health score
- `v_expense_forecast` - Expense forecasting with moving averages
- `v_kpi_summary` - Dashboard KPI metrics
- `v_transaction_comparison` - YoY/MoM transaction comparisons

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

## 📊 Phase 3: BI Views & Superset Setup

### Automatic Setup (Recommended)

Run the initialization script to automatically set up Superset with pre-configured datasets, charts, and dashboards:

**Windows (PowerShell):**
```powershell
.\scripts\init-superset.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/init-superset.sh
./scripts/init-superset.sh
```

### Manual Setup

1. Start all services:
   ```bash
   docker-compose up -d
   ```

2. Access Superset at http://localhost:8088
3. Login with admin / admin
4. Add Database connection:
   - Click **Settings** → **Database Connections** → **+ Database**
   - Database: PostgreSQL
   - Host: `postgres`
   - Port: `5432`
   - Database: `finance_db`
   - User: `superset_readonly`
   - Password: `superset_pass`

5. Create datasets from the analytical views:
   - Navigate to **Data** → **Datasets** → **+ Dataset**
   - Select the Finance Database
   - Add each `v_*` view as a dataset

6. Build charts and dashboards using the pre-defined JSON templates in `superset/dashboards/`

### Pre-built Dashboard

The **Personal Finance Dashboard** includes:
- 📊 KPI Cards: MTD Income, Expense, Savings, Balance
- 📈 Monthly Cashflow Trend (Line Chart)
- 🥧 Expense by Category (Pie Chart)
- 📊 Budget vs Actual (Bar Chart)
- 📉 Savings Rate Trend (Line Chart)
- 📅 Spending by Day of Week (Bar Chart)
- 💰 Wallet Balances (Donut Chart)
- 📋 Top Spending Categories (Table)
- 📈 Weekly Expense Trend (Area Chart)

### BI Views Available

| View | Description | Use Case |
|------|-------------|----------|
| `v_kpi_summary` | Dashboard KPIs | Summary cards |
| `v_monthly_cashflow` | Monthly trends with MoM | Trend analysis |
| `v_category_breakdown` | Category spending | Pie charts |
| `v_budget_performance` | Budget tracking | Progress bars |
| `v_savings_rate` | Savings analysis | Gauge charts |
| `v_weekly_trends` | Weekly patterns | Line charts |
| `v_spending_by_day_of_week` | Day patterns | Heatmaps |
| `v_expense_forecast` | Spending forecasts | Predictions |
| `v_user_financial_health` | Health score | Scorecards |

## ⚡ Phase 4: n8n Automation Setup

### Pre-built Workflows

The system includes 2 automation workflows located in `n8n/workflows/`:

| Workflow | File | Trigger | Description |
|----------|------|---------|-------------|
| Monthly Bill Reminder | `monthly_bill_reminder.json` | Cron (1st of month) + Manual | Sends email reminders for upcoming bills |
| Budget Overrun Alert | `budget_overrun_alert.json` | Cron (Daily 9AM) + Manual | Alerts users when spending exceeds budget |

### Step-by-Step Import Instructions

#### 1. Access n8n
- URL: http://localhost:5678
- Login: admin / admin

#### 2. Create Required Credentials

**A) MailHog SMTP Credential:**
1. Go to **Settings** → **Credentials** → **Add Credential**
2. Search for **SMTP**
3. Configure:
   - **Credential Name**: `MailHog SMTP`
   - **Host**: `mailhog`
   - **Port**: `1025`
   - **SSL/TLS**: OFF
   - **User**: (leave empty)
   - **Password**: (leave empty)
4. Click **Save**

**B) PostgreSQL Credential (for Budget Overrun workflow):**
1. Go to **Settings** → **Credentials** → **Add Credential**
2. Search for **Postgres**
3. Configure:
   - **Credential Name**: `Finance PostgreSQL`
   - **Host**: `postgres`
   - **Port**: `5432`
   - **Database**: `finance_db`
   - **User**: `n8n_readonly`
   - **Password**: `n8n_pass`
   - **SSL**: OFF
4. Click **Save**

#### 3. Import Workflows

1. Go to **Workflows** → **Add Workflow** → **Import from File**
2. Import `n8n/workflows/monthly_bill_reminder.json`
3. Repeat for `n8n/workflows/budget_overrun_alert.json`

#### 4. Connect Credentials to Nodes

After importing each workflow:

1. Open the workflow
2. Click on the **Send Email** node
3. Select the **MailHog SMTP** credential
4. For Budget Overrun workflow: click on **Query Budget Overruns** node and select **Finance PostgreSQL** credential
5. Click **Save**
6. Toggle **Active** to enable the workflow

### Testing the Workflows

#### Test Monthly Bill Reminder:
1. Open the **Monthly Bill Reminder** workflow
2. Click **Execute Workflow** (or click the Manual Trigger node)
3. Check MailHog UI at http://localhost:8025 for sent emails

#### Test Budget Overrun Alert:
1. First, ensure there are budget overruns in the database:
   ```sql
   -- Connect to postgres and add test data if needed
   -- The seed data should already have some budget overruns for demo@finance.app
   ```
2. Open the **Budget Overrun Alert** workflow
3. Click **Execute Workflow**
4. Check MailHog UI at http://localhost:8025 for alert emails

### Workflow Details

#### Monthly Bill Reminder
- **Schedule**: 1st of each month at 8:00 AM
- **Data Source**: Backend API `/api/automation/bills/upcoming?month=YYYY-MM`
- **Email Content**:
  - Bill name
  - Due date
  - Amount
  - Wallet
  - Category
  - Total monthly bills

#### Budget Overrun Alert
- **Schedule**: Daily at 9:00 AM
- **Data Source**: PostgreSQL view `v_budget_vs_actual`
- **Email Content**:
  - Category name
  - Budget amount
  - Actual spent
  - Overrun amount
  - Usage percentage
  - Recommendations

### API Endpoints for Automation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/automation/bills/upcoming` | GET | Get upcoming bills for a month |
| `/api/automation/budget/overruns` | GET | Get current budget overruns |
| `/api/automation/health` | GET | Health check |

**Query Parameters:**
- `service_key`: Required authentication key (from env `N8N_SERVICE_KEY`)
- `month`: For bills endpoint, format `YYYY-MM`
- `year`, `month`: For budget endpoint (optional, defaults to current)

### Viewing Sent Emails

MailHog captures all emails sent by n8n:
- URL: http://localhost:8025
- All workflow emails appear here for testing

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
