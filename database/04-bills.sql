-- ============================================
-- Personal Finance BI System - Bills Table
-- Phase 4: Automation Support
-- ============================================

-- Bills table for recurring bill tracking
CREATE TABLE IF NOT EXISTS bills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    wallet_id INTEGER NOT NULL REFERENCES wallets(id) ON DELETE RESTRICT,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    name VARCHAR(200) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),
    due_day INTEGER NOT NULL CHECK (due_day BETWEEN 1 AND 31),
    is_recurring BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    description VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bills_user ON bills(user_id);
CREATE INDEX IF NOT EXISTS idx_bills_due_day ON bills(due_day);
CREATE INDEX IF NOT EXISTS idx_bills_active ON bills(is_active);

-- ============================================
-- View: Upcoming Bills for a Month
-- ============================================

CREATE OR REPLACE VIEW v_upcoming_bills AS
SELECT 
    b.id AS bill_id,
    b.user_id,
    u.email AS user_email,
    u.full_name AS user_name,
    b.name AS bill_name,
    b.amount,
    b.due_day,
    b.description,
    w.name AS wallet_name,
    w.currency,
    c.name AS category_name,
    c.icon AS category_icon,
    c.color AS category_color,
    b.is_recurring,
    b.is_active
FROM bills b
JOIN users u ON b.user_id = u.id
JOIN wallets w ON b.wallet_id = w.id
JOIN categories c ON b.category_id = c.id
WHERE b.is_active = TRUE;

-- ============================================
-- View: Budget Overruns for Alerts
-- ============================================

CREATE OR REPLACE VIEW v_budget_overruns AS
SELECT 
    bva.user_id,
    u.email AS user_email,
    u.full_name AS user_name,
    bva.year,
    bva.month,
    TO_CHAR(MAKE_DATE(bva.year, bva.month, 1), 'YYYY-MM') AS period,
    bva.category_id,
    bva.category_name,
    bva.category_color,
    bva.budget_amount,
    bva.actual_spent,
    bva.actual_spent - bva.budget_amount AS overrun_amount,
    bva.usage_percentage,
    bva.status
FROM v_budget_vs_actual bva
JOIN users u ON bva.user_id = u.id
WHERE bva.actual_spent > bva.budget_amount;

-- ============================================
-- Demo Bills Data
-- ============================================

INSERT INTO bills (user_id, wallet_id, category_id, name, amount, due_day, description) VALUES
    -- User 1 bills
    (1, 2, 5, 'Tiền điện', 500000, 15, 'Hóa đơn tiền điện hàng tháng'),
    (1, 2, 5, 'Tiền nước', 200000, 20, 'Hóa đơn tiền nước'),
    (1, 2, 5, 'Internet FPT', 300000, 25, 'Gói internet cáp quang'),
    (1, 3, 5, 'Điện thoại', 150000, 10, 'Gói cước di động'),
    (1, 2, 5, 'Netflix', 260000, 5, 'Gói Premium'),
    (1, 2, 5, 'Spotify', 59000, 5, 'Gói Premium Individual'),
    (1, 2, 5, 'Phí quản lý chung cư', 1500000, 1, 'Phí dịch vụ tòa nhà'),
    -- User 2 bills
    (2, 5, 5, 'Electricity Bill', 400000, 15, 'Monthly electricity'),
    (2, 5, 5, 'Water Bill', 150000, 20, 'Monthly water'),
    (2, 5, 5, 'Internet', 250000, 25, 'Fiber internet package')
ON CONFLICT DO NOTHING;

-- Grant permissions
GRANT SELECT ON bills TO superset_readonly;
GRANT SELECT ON v_upcoming_bills TO superset_readonly;
GRANT SELECT ON v_budget_overruns TO superset_readonly;

GRANT SELECT ON bills TO n8n_readonly;
GRANT SELECT ON v_upcoming_bills TO n8n_readonly;
GRANT SELECT ON v_budget_overruns TO n8n_readonly;

-- ============================================
-- Bills Table Complete!
-- ============================================
