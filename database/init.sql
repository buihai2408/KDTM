-- ============================================
-- Personal Finance BI System - Database Schema
-- ============================================

-- ============================================
-- 1. CORE TABLES
-- ============================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Categories table (system defaults + user custom)
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    icon VARCHAR(50) DEFAULT 'tag',
    color VARCHAR(7) DEFAULT '#6366f1',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_categories_user ON categories(user_id);
CREATE INDEX IF NOT EXISTS idx_categories_type ON categories(type);

-- Wallets table
CREATE TABLE IF NOT EXISTS wallets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    balance DECIMAL(15, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'VND',
    icon VARCHAR(50) DEFAULT 'wallet',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_wallet_name_per_user UNIQUE(user_id, name)
);

CREATE INDEX IF NOT EXISTS idx_wallets_user ON wallets(user_id);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    wallet_id INTEGER NOT NULL REFERENCES wallets(id) ON DELETE RESTRICT,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),
    description VARCHAR(500),
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);

-- Budgets table
CREATE TABLE IF NOT EXISTS budgets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    year INTEGER NOT NULL CHECK (year >= 2020),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_budget UNIQUE(user_id, category_id, month, year)
);

CREATE INDEX IF NOT EXISTS idx_budgets_user_period ON budgets(user_id, year, month);

-- ============================================
-- 2. DEFAULT CATEGORIES (System-wide)
-- ============================================

INSERT INTO categories (user_id, name, type, icon, color) VALUES
    -- Expense categories (user_id = NULL for system defaults)
    (NULL, 'Food & Dining', 'expense', 'utensils', '#ef4444'),
    (NULL, 'Transportation', 'expense', 'car', '#f97316'),
    (NULL, 'Shopping', 'expense', 'shopping-bag', '#eab308'),
    (NULL, 'Entertainment', 'expense', 'film', '#22c55e'),
    (NULL, 'Bills & Utilities', 'expense', 'file-text', '#3b82f6'),
    (NULL, 'Healthcare', 'expense', 'heart-pulse', '#ec4899'),
    (NULL, 'Education', 'expense', 'graduation-cap', '#8b5cf6'),
    (NULL, 'Other Expense', 'expense', 'more-horizontal', '#6b7280'),
    -- Income categories
    (NULL, 'Salary', 'income', 'briefcase', '#10b981'),
    (NULL, 'Freelance', 'income', 'laptop', '#06b6d4'),
    (NULL, 'Investment', 'income', 'trending-up', '#8b5cf6'),
    (NULL, 'Gift', 'income', 'gift', '#f43f5e'),
    (NULL, 'Other Income', 'income', 'plus-circle', '#6b7280')
ON CONFLICT DO NOTHING;

-- ============================================
-- 3. TRIGGER: Auto-update wallet balance
-- ============================================

CREATE OR REPLACE FUNCTION update_wallet_balance()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.type = 'income' THEN
            UPDATE wallets SET balance = balance + NEW.amount WHERE id = NEW.wallet_id;
        ELSE
            UPDATE wallets SET balance = balance - NEW.amount WHERE id = NEW.wallet_id;
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        IF OLD.type = 'income' THEN
            UPDATE wallets SET balance = balance - OLD.amount WHERE id = OLD.wallet_id;
        ELSE
            UPDATE wallets SET balance = balance + OLD.amount WHERE id = OLD.wallet_id;
        END IF;
    ELSIF TG_OP = 'UPDATE' THEN
        -- Revert old transaction
        IF OLD.type = 'income' THEN
            UPDATE wallets SET balance = balance - OLD.amount WHERE id = OLD.wallet_id;
        ELSE
            UPDATE wallets SET balance = balance + OLD.amount WHERE id = OLD.wallet_id;
        END IF;
        -- Apply new transaction
        IF NEW.type = 'income' THEN
            UPDATE wallets SET balance = balance + NEW.amount WHERE id = NEW.wallet_id;
        ELSE
            UPDATE wallets SET balance = balance - NEW.amount WHERE id = NEW.wallet_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_wallet_balance ON transactions;
CREATE TRIGGER trg_update_wallet_balance
    AFTER INSERT OR UPDATE OR DELETE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_wallet_balance();

-- ============================================
-- 4. ANALYTICAL VIEWS (For Superset & Dify)
-- ============================================

-- View: Daily Summary
CREATE OR REPLACE VIEW v_daily_summary AS
SELECT 
    t.user_id,
    t.transaction_date,
    t.type,
    COUNT(*) AS transaction_count,
    SUM(t.amount) AS total_amount
FROM transactions t
GROUP BY t.user_id, t.transaction_date, t.type;

-- View: Monthly Summary
CREATE OR REPLACE VIEW v_monthly_summary AS
SELECT 
    t.user_id,
    EXTRACT(YEAR FROM t.transaction_date)::INTEGER AS year,
    EXTRACT(MONTH FROM t.transaction_date)::INTEGER AS month,
    DATE_TRUNC('month', t.transaction_date)::DATE AS month_start,
    t.type,
    COUNT(*) AS transaction_count,
    SUM(t.amount) AS total_amount,
    AVG(t.amount) AS avg_amount,
    MAX(t.amount) AS max_amount
FROM transactions t
GROUP BY 
    t.user_id,
    EXTRACT(YEAR FROM t.transaction_date),
    EXTRACT(MONTH FROM t.transaction_date),
    DATE_TRUNC('month', t.transaction_date),
    t.type;

-- View: Category Breakdown
CREATE OR REPLACE VIEW v_category_breakdown AS
SELECT 
    t.user_id,
    EXTRACT(YEAR FROM t.transaction_date)::INTEGER AS year,
    EXTRACT(MONTH FROM t.transaction_date)::INTEGER AS month,
    t.type,
    c.id AS category_id,
    c.name AS category_name,
    c.icon AS category_icon,
    c.color AS category_color,
    COUNT(*) AS transaction_count,
    SUM(t.amount) AS total_amount,
    ROUND(
        SUM(t.amount) * 100.0 / 
        NULLIF(SUM(SUM(t.amount)) OVER (PARTITION BY t.user_id, t.type, 
            EXTRACT(YEAR FROM t.transaction_date), 
            EXTRACT(MONTH FROM t.transaction_date)), 0)
    , 2) AS percentage
FROM transactions t
JOIN categories c ON t.category_id = c.id
GROUP BY 
    t.user_id,
    EXTRACT(YEAR FROM t.transaction_date),
    EXTRACT(MONTH FROM t.transaction_date),
    t.type,
    c.id, c.name, c.icon, c.color;

-- View: Income vs Expense
CREATE OR REPLACE VIEW v_income_vs_expense AS
SELECT 
    user_id,
    year,
    month,
    month_start,
    COALESCE(SUM(CASE WHEN type = 'income' THEN total_amount END), 0) AS total_income,
    COALESCE(SUM(CASE WHEN type = 'expense' THEN total_amount END), 0) AS total_expense,
    COALESCE(SUM(CASE WHEN type = 'income' THEN total_amount END), 0) - 
    COALESCE(SUM(CASE WHEN type = 'expense' THEN total_amount END), 0) AS net_savings,
    CASE 
        WHEN COALESCE(SUM(CASE WHEN type = 'income' THEN total_amount END), 0) > 0
        THEN ROUND(
            COALESCE(SUM(CASE WHEN type = 'expense' THEN total_amount END), 0) * 100.0 / 
            COALESCE(SUM(CASE WHEN type = 'income' THEN total_amount END), 1)
        , 2)
        ELSE 0
    END AS expense_ratio
FROM v_monthly_summary
GROUP BY user_id, year, month, month_start;

-- View: Budget vs Actual
CREATE OR REPLACE VIEW v_budget_vs_actual AS
SELECT 
    b.user_id,
    b.year,
    b.month,
    b.category_id,
    c.name AS category_name,
    c.icon AS category_icon,
    c.color AS category_color,
    b.amount AS budget_amount,
    COALESCE(actual.spent, 0) AS actual_spent,
    b.amount - COALESCE(actual.spent, 0) AS remaining,
    ROUND(COALESCE(actual.spent, 0) * 100.0 / NULLIF(b.amount, 0), 2) AS usage_percentage,
    CASE 
        WHEN COALESCE(actual.spent, 0) >= b.amount THEN 'exceeded'
        WHEN COALESCE(actual.spent, 0) >= b.amount * 0.8 THEN 'warning'
        ELSE 'safe'
    END AS status
FROM budgets b
JOIN categories c ON b.category_id = c.id
LEFT JOIN (
    SELECT 
        user_id,
        category_id,
        EXTRACT(YEAR FROM transaction_date)::INTEGER AS year,
        EXTRACT(MONTH FROM transaction_date)::INTEGER AS month,
        SUM(amount) AS spent
    FROM transactions
    WHERE type = 'expense'
    GROUP BY user_id, category_id, 
        EXTRACT(YEAR FROM transaction_date),
        EXTRACT(MONTH FROM transaction_date)
) actual ON b.user_id = actual.user_id 
    AND b.category_id = actual.category_id 
    AND b.year = actual.year 
    AND b.month = actual.month;

-- View: Wallet Balance
CREATE OR REPLACE VIEW v_wallet_balance AS
SELECT 
    w.id AS wallet_id,
    w.user_id,
    w.name AS wallet_name,
    w.icon AS wallet_icon,
    w.currency,
    w.balance AS current_balance,
    COALESCE(stats.total_income, 0) AS total_income,
    COALESCE(stats.total_expense, 0) AS total_expense,
    COALESCE(stats.transaction_count, 0) AS transaction_count,
    stats.last_transaction_date
FROM wallets w
LEFT JOIN (
    SELECT 
        wallet_id,
        SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS total_income,
        SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS total_expense,
        COUNT(*) AS transaction_count,
        MAX(transaction_date) AS last_transaction_date
    FROM transactions
    GROUP BY wallet_id
) stats ON w.id = stats.wallet_id
WHERE w.is_active = TRUE;

-- View: Recent Transactions (with details)
CREATE OR REPLACE VIEW v_recent_transactions AS
SELECT 
    t.id AS transaction_id,
    t.user_id,
    t.type,
    t.amount,
    t.description,
    t.transaction_date,
    c.name AS category_name,
    c.icon AS category_icon,
    c.color AS category_color,
    w.name AS wallet_name,
    t.created_at
FROM transactions t
JOIN categories c ON t.category_id = c.id
JOIN wallets w ON t.wallet_id = w.id;

-- ============================================
-- 5. READ-ONLY USERS (For Superset & n8n)
-- ============================================

-- Create read-only user for Superset
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'superset_readonly') THEN
        CREATE USER superset_readonly WITH PASSWORD 'superset_pass';
    END IF;
END
$$;

GRANT USAGE ON SCHEMA public TO superset_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO superset_readonly;

-- Create read-only user for n8n
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'n8n_readonly') THEN
        CREATE USER n8n_readonly WITH PASSWORD 'n8n_pass';
    END IF;
END
$$;

GRANT USAGE ON SCHEMA public TO n8n_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO n8n_readonly;

-- ============================================
-- Schema initialization complete!
-- ============================================
