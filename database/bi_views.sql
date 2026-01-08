-- ============================================
-- Personal Finance BI System - Advanced BI Views
-- Phase 3: Enhanced Analytics for Superset
-- ============================================

-- ============================================
-- 1. TIME DIMENSION TABLE (For better date analysis)
-- ============================================

CREATE TABLE IF NOT EXISTS dim_date (
    date_key DATE PRIMARY KEY,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    week_of_year INTEGER,
    day_of_month INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(20),
    is_weekend BOOLEAN,
    is_month_start BOOLEAN,
    is_month_end BOOLEAN,
    fiscal_year INTEGER,
    fiscal_quarter INTEGER
);

-- Populate date dimension (5 years of data)
INSERT INTO dim_date (date_key, year, quarter, month, month_name, week_of_year, 
    day_of_month, day_of_week, day_name, is_weekend, is_month_start, is_month_end,
    fiscal_year, fiscal_quarter)
SELECT 
    d::DATE as date_key,
    EXTRACT(YEAR FROM d)::INTEGER as year,
    EXTRACT(QUARTER FROM d)::INTEGER as quarter,
    EXTRACT(MONTH FROM d)::INTEGER as month,
    TO_CHAR(d, 'Month') as month_name,
    EXTRACT(WEEK FROM d)::INTEGER as week_of_year,
    EXTRACT(DAY FROM d)::INTEGER as day_of_month,
    EXTRACT(DOW FROM d)::INTEGER as day_of_week,
    TO_CHAR(d, 'Day') as day_name,
    EXTRACT(DOW FROM d) IN (0, 6) as is_weekend,
    EXTRACT(DAY FROM d) = 1 as is_month_start,
    d = (DATE_TRUNC('month', d) + INTERVAL '1 month - 1 day')::DATE as is_month_end,
    CASE WHEN EXTRACT(MONTH FROM d) >= 4 
         THEN EXTRACT(YEAR FROM d)::INTEGER 
         ELSE (EXTRACT(YEAR FROM d) - 1)::INTEGER 
    END as fiscal_year,
    CASE 
        WHEN EXTRACT(MONTH FROM d) IN (4,5,6) THEN 1
        WHEN EXTRACT(MONTH FROM d) IN (7,8,9) THEN 2
        WHEN EXTRACT(MONTH FROM d) IN (10,11,12) THEN 3
        ELSE 4
    END as fiscal_quarter
FROM generate_series(
    CURRENT_DATE - INTERVAL '3 years',
    CURRENT_DATE + INTERVAL '2 years',
    INTERVAL '1 day'
) d
ON CONFLICT (date_key) DO NOTHING;

-- ============================================
-- 2. ENHANCED TRANSACTION FACT VIEW
-- ============================================

CREATE OR REPLACE VIEW v_fact_transactions AS
SELECT 
    t.id AS transaction_id,
    t.user_id,
    t.wallet_id,
    t.category_id,
    t.type AS transaction_type,
    t.amount,
    t.description,
    t.transaction_date,
    t.created_at,
    
    -- Date dimensions
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    d.week_of_year,
    d.day_of_week,
    d.day_name,
    d.is_weekend,
    
    -- Category details
    c.name AS category_name,
    c.icon AS category_icon,
    c.color AS category_color,
    c.type AS category_type,
    
    -- Wallet details
    w.name AS wallet_name,
    w.currency,
    
    -- User details
    u.full_name AS user_name,
    u.email AS user_email,
    
    -- Computed metrics
    CASE WHEN t.type = 'income' THEN t.amount ELSE 0 END AS income_amount,
    CASE WHEN t.type = 'expense' THEN t.amount ELSE 0 END AS expense_amount,
    
    -- Time of day analysis
    EXTRACT(HOUR FROM t.created_at)::INTEGER AS hour_of_day,
    CASE 
        WHEN EXTRACT(HOUR FROM t.created_at) < 6 THEN 'Night'
        WHEN EXTRACT(HOUR FROM t.created_at) < 12 THEN 'Morning'
        WHEN EXTRACT(HOUR FROM t.created_at) < 18 THEN 'Afternoon'
        ELSE 'Evening'
    END AS time_of_day

FROM transactions t
JOIN dim_date d ON t.transaction_date = d.date_key
JOIN categories c ON t.category_id = c.id
JOIN wallets w ON t.wallet_id = w.id
JOIN users u ON t.user_id = u.id;

-- ============================================
-- 3. WEEKLY TREND ANALYSIS
-- ============================================

CREATE OR REPLACE VIEW v_weekly_trends AS
SELECT 
    t.user_id,
    d.year,
    d.week_of_year,
    DATE_TRUNC('week', t.transaction_date)::DATE AS week_start,
    DATE_TRUNC('week', t.transaction_date)::DATE + INTERVAL '6 days' AS week_end,
    t.type,
    COUNT(*) AS transaction_count,
    SUM(t.amount) AS total_amount,
    AVG(t.amount) AS avg_amount,
    MIN(t.amount) AS min_amount,
    MAX(t.amount) AS max_amount,
    COUNT(DISTINCT t.category_id) AS categories_used,
    COUNT(DISTINCT t.wallet_id) AS wallets_used
FROM transactions t
JOIN dim_date d ON t.transaction_date = d.date_key
GROUP BY 
    t.user_id, 
    d.year, 
    d.week_of_year, 
    DATE_TRUNC('week', t.transaction_date),
    t.type;

-- ============================================
-- 4. SPENDING PATTERN ANALYSIS (Day of Week)
-- ============================================

CREATE OR REPLACE VIEW v_spending_by_day_of_week AS
SELECT 
    t.user_id,
    d.day_of_week,
    d.day_name,
    d.is_weekend,
    t.type,
    COUNT(*) AS transaction_count,
    SUM(t.amount) AS total_amount,
    AVG(t.amount) AS avg_amount,
    ROUND(COUNT(*)::NUMERIC / COUNT(DISTINCT t.transaction_date), 2) AS avg_daily_transactions
FROM transactions t
JOIN dim_date d ON t.transaction_date = d.date_key
GROUP BY t.user_id, d.day_of_week, d.day_name, d.is_weekend, t.type
ORDER BY t.user_id, d.day_of_week;

-- ============================================
-- 5. SPENDING PATTERN ANALYSIS (Hour of Day)
-- ============================================

CREATE OR REPLACE VIEW v_spending_by_hour AS
SELECT 
    t.user_id,
    EXTRACT(HOUR FROM t.created_at)::INTEGER AS hour_of_day,
    CASE 
        WHEN EXTRACT(HOUR FROM t.created_at) < 6 THEN 'Night (0-5)'
        WHEN EXTRACT(HOUR FROM t.created_at) < 12 THEN 'Morning (6-11)'
        WHEN EXTRACT(HOUR FROM t.created_at) < 18 THEN 'Afternoon (12-17)'
        ELSE 'Evening (18-23)'
    END AS time_period,
    t.type,
    COUNT(*) AS transaction_count,
    SUM(t.amount) AS total_amount,
    AVG(t.amount) AS avg_amount
FROM transactions t
WHERE t.type = 'expense'
GROUP BY 
    t.user_id, 
    EXTRACT(HOUR FROM t.created_at),
    t.type
ORDER BY t.user_id, hour_of_day;

-- ============================================
-- 6. MONTHLY CASHFLOW ANALYSIS
-- ============================================

CREATE OR REPLACE VIEW v_monthly_cashflow AS
SELECT 
    user_id,
    year,
    month,
    month_start,
    total_income,
    total_expense,
    net_savings,
    expense_ratio,
    
    -- Month-over-Month changes
    LAG(total_income) OVER (PARTITION BY user_id ORDER BY year, month) AS prev_month_income,
    LAG(total_expense) OVER (PARTITION BY user_id ORDER BY year, month) AS prev_month_expense,
    LAG(net_savings) OVER (PARTITION BY user_id ORDER BY year, month) AS prev_month_savings,
    
    -- Change percentages
    CASE 
        WHEN LAG(total_income) OVER (PARTITION BY user_id ORDER BY year, month) > 0
        THEN ROUND((total_income - LAG(total_income) OVER (PARTITION BY user_id ORDER BY year, month)) * 100.0 / 
            LAG(total_income) OVER (PARTITION BY user_id ORDER BY year, month), 2)
        ELSE 0
    END AS income_change_pct,
    
    CASE 
        WHEN LAG(total_expense) OVER (PARTITION BY user_id ORDER BY year, month) > 0
        THEN ROUND((total_expense - LAG(total_expense) OVER (PARTITION BY user_id ORDER BY year, month)) * 100.0 / 
            LAG(total_expense) OVER (PARTITION BY user_id ORDER BY year, month), 2)
        ELSE 0
    END AS expense_change_pct,
    
    -- Running totals (YTD)
    SUM(total_income) OVER (PARTITION BY user_id, year ORDER BY month) AS ytd_income,
    SUM(total_expense) OVER (PARTITION BY user_id, year ORDER BY month) AS ytd_expense,
    SUM(net_savings) OVER (PARTITION BY user_id, year ORDER BY month) AS ytd_savings,
    
    -- 3-month moving average
    ROUND(AVG(total_expense) OVER (
        PARTITION BY user_id ORDER BY year, month 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS expense_3m_avg,
    
    ROUND(AVG(total_income) OVER (
        PARTITION BY user_id ORDER BY year, month 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS income_3m_avg

FROM v_income_vs_expense
ORDER BY user_id, year, month;

-- ============================================
-- 7. CATEGORY GROWTH ANALYSIS
-- ============================================

CREATE OR REPLACE VIEW v_category_growth AS
WITH monthly_category AS (
    SELECT 
        t.user_id,
        c.id AS category_id,
        c.name AS category_name,
        c.type AS category_type,
        c.color AS category_color,
        EXTRACT(YEAR FROM t.transaction_date)::INTEGER AS year,
        EXTRACT(MONTH FROM t.transaction_date)::INTEGER AS month,
        DATE_TRUNC('month', t.transaction_date)::DATE AS month_start,
        COUNT(*) AS transaction_count,
        SUM(t.amount) AS total_amount
    FROM transactions t
    JOIN categories c ON t.category_id = c.id
    GROUP BY 
        t.user_id, c.id, c.name, c.type, c.color,
        EXTRACT(YEAR FROM t.transaction_date),
        EXTRACT(MONTH FROM t.transaction_date),
        DATE_TRUNC('month', t.transaction_date)
)
SELECT 
    *,
    LAG(total_amount) OVER (PARTITION BY user_id, category_id ORDER BY year, month) AS prev_month_amount,
    total_amount - COALESCE(LAG(total_amount) OVER (PARTITION BY user_id, category_id ORDER BY year, month), 0) AS amount_change,
    CASE 
        WHEN LAG(total_amount) OVER (PARTITION BY user_id, category_id ORDER BY year, month) > 0
        THEN ROUND((total_amount - LAG(total_amount) OVER (PARTITION BY user_id, category_id ORDER BY year, month)) * 100.0 /
            LAG(total_amount) OVER (PARTITION BY user_id, category_id ORDER BY year, month), 2)
        ELSE 0
    END AS growth_pct
FROM monthly_category;

-- ============================================
-- 8. TOP SPENDING CATEGORIES (RANKED)
-- ============================================

CREATE OR REPLACE VIEW v_top_categories AS
WITH category_totals AS (
    SELECT 
        t.user_id,
        EXTRACT(YEAR FROM t.transaction_date)::INTEGER AS year,
        EXTRACT(MONTH FROM t.transaction_date)::INTEGER AS month,
        DATE_TRUNC('month', t.transaction_date)::DATE AS month_start,
        c.id AS category_id,
        c.name AS category_name,
        c.color AS category_color,
        c.icon AS category_icon,
        t.type,
        SUM(t.amount) AS total_amount,
        COUNT(*) AS transaction_count
    FROM transactions t
    JOIN categories c ON t.category_id = c.id
    GROUP BY 
        t.user_id,
        EXTRACT(YEAR FROM t.transaction_date),
        EXTRACT(MONTH FROM t.transaction_date),
        DATE_TRUNC('month', t.transaction_date),
        c.id, c.name, c.color, c.icon, t.type
)
SELECT 
    *,
    RANK() OVER (PARTITION BY user_id, year, month, type ORDER BY total_amount DESC) AS rank_in_type,
    ROUND(total_amount * 100.0 / SUM(total_amount) OVER (PARTITION BY user_id, year, month, type), 2) AS percentage_of_type
FROM category_totals;

-- ============================================
-- 9. BUDGET PERFORMANCE METRICS
-- ============================================

CREATE OR REPLACE VIEW v_budget_performance AS
SELECT 
    bva.*,
    
    -- Performance indicators
    CASE 
        WHEN usage_percentage >= 100 THEN 'Over Budget'
        WHEN usage_percentage >= 90 THEN 'Critical'
        WHEN usage_percentage >= 75 THEN 'Warning'
        WHEN usage_percentage >= 50 THEN 'On Track'
        ELSE 'Under Utilized'
    END AS performance_status,
    
    -- Days remaining in month
    (DATE_TRUNC('month', MAKE_DATE(year, month, 1)) + INTERVAL '1 month' - INTERVAL '1 day')::DATE - CURRENT_DATE AS days_remaining,
    
    -- Daily budget rate
    ROUND(budget_amount / EXTRACT(DAY FROM (DATE_TRUNC('month', MAKE_DATE(year, month, 1)) + INTERVAL '1 month' - INTERVAL '1 day'))::NUMERIC, 2) AS daily_budget,
    
    -- Projected spending (if same rate continues)
    CASE 
        WHEN EXTRACT(DAY FROM CURRENT_DATE) > 0 
        THEN ROUND(actual_spent * EXTRACT(DAY FROM (DATE_TRUNC('month', MAKE_DATE(year, month, 1)) + INTERVAL '1 month' - INTERVAL '1 day'))::NUMERIC / 
            GREATEST(EXTRACT(DAY FROM CURRENT_DATE)::NUMERIC, 1), 2)
        ELSE 0
    END AS projected_spending,
    
    -- Safe daily spending remaining
    CASE 
        WHEN (DATE_TRUNC('month', MAKE_DATE(year, month, 1)) + INTERVAL '1 month' - INTERVAL '1 day')::DATE - CURRENT_DATE > 0
        THEN ROUND(remaining / GREATEST(((DATE_TRUNC('month', MAKE_DATE(year, month, 1)) + INTERVAL '1 month' - INTERVAL '1 day')::DATE - CURRENT_DATE)::NUMERIC, 1), 2)
        ELSE 0
    END AS safe_daily_spend

FROM v_budget_vs_actual bva
WHERE MAKE_DATE(year, month, 1) <= CURRENT_DATE;

-- ============================================
-- 10. SAVINGS RATE ANALYSIS
-- ============================================

CREATE OR REPLACE VIEW v_savings_rate AS
SELECT 
    user_id,
    year,
    month,
    month_start,
    total_income,
    total_expense,
    net_savings,
    
    -- Savings rate (percentage of income saved)
    CASE 
        WHEN total_income > 0 
        THEN ROUND(net_savings * 100.0 / total_income, 2)
        ELSE 0
    END AS savings_rate,
    
    -- Savings rate category
    CASE 
        WHEN total_income = 0 THEN 'No Income'
        WHEN net_savings * 100.0 / total_income >= 50 THEN 'Excellent (50%+)'
        WHEN net_savings * 100.0 / total_income >= 30 THEN 'Great (30-50%)'
        WHEN net_savings * 100.0 / total_income >= 20 THEN 'Good (20-30%)'
        WHEN net_savings * 100.0 / total_income >= 10 THEN 'Fair (10-20%)'
        WHEN net_savings * 100.0 / total_income >= 0 THEN 'Low (0-10%)'
        ELSE 'Negative'
    END AS savings_category,
    
    -- Cumulative savings
    SUM(net_savings) OVER (PARTITION BY user_id ORDER BY year, month) AS cumulative_savings,
    
    -- Average savings rate (rolling 3 months)
    ROUND(AVG(CASE WHEN total_income > 0 THEN net_savings * 100.0 / total_income ELSE 0 END) 
        OVER (PARTITION BY user_id ORDER BY year, month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS rolling_3m_savings_rate

FROM v_income_vs_expense;

-- ============================================
-- 11. WALLET ANALYTICS
-- ============================================

CREATE OR REPLACE VIEW v_wallet_analytics AS
SELECT 
    w.id AS wallet_id,
    w.user_id,
    w.name AS wallet_name,
    w.currency,
    w.balance AS current_balance,
    w.created_at AS wallet_created,
    
    -- Transaction statistics
    COUNT(t.id) AS total_transactions,
    COUNT(CASE WHEN t.type = 'income' THEN 1 END) AS income_count,
    COUNT(CASE WHEN t.type = 'expense' THEN 1 END) AS expense_count,
    
    -- Amounts
    COALESCE(SUM(CASE WHEN t.type = 'income' THEN t.amount END), 0) AS total_income,
    COALESCE(SUM(CASE WHEN t.type = 'expense' THEN t.amount END), 0) AS total_expense,
    
    -- Averages
    ROUND(AVG(CASE WHEN t.type = 'expense' THEN t.amount END), 2) AS avg_expense,
    ROUND(AVG(CASE WHEN t.type = 'income' THEN t.amount END), 2) AS avg_income,
    
    -- Time metrics
    MIN(t.transaction_date) AS first_transaction,
    MAX(t.transaction_date) AS last_transaction,
    CURRENT_DATE - MAX(t.transaction_date) AS days_since_last_transaction,
    
    -- Activity status
    CASE 
        WHEN MAX(t.transaction_date) >= CURRENT_DATE - INTERVAL '7 days' THEN 'Very Active'
        WHEN MAX(t.transaction_date) >= CURRENT_DATE - INTERVAL '30 days' THEN 'Active'
        WHEN MAX(t.transaction_date) >= CURRENT_DATE - INTERVAL '90 days' THEN 'Moderate'
        ELSE 'Inactive'
    END AS activity_status
    
FROM wallets w
LEFT JOIN transactions t ON w.id = t.wallet_id
WHERE w.is_active = TRUE
GROUP BY w.id, w.user_id, w.name, w.currency, w.balance, w.created_at;

-- ============================================
-- 12. USER FINANCIAL HEALTH SCORE
-- ============================================

CREATE OR REPLACE VIEW v_user_financial_health AS
WITH user_metrics AS (
    SELECT 
        u.id AS user_id,
        u.full_name,
        u.email,
        
        -- Current month metrics
        COALESCE(cm.total_income, 0) AS current_month_income,
        COALESCE(cm.total_expense, 0) AS current_month_expense,
        COALESCE(cm.net_savings, 0) AS current_month_savings,
        
        -- Budget adherence (avg % within budget)
        COALESCE(ba.avg_budget_adherence, 100) AS budget_adherence,
        
        -- Wallet balance
        COALESCE(wb.total_balance, 0) AS total_balance,
        
        -- Transaction diversity
        COALESCE(td.category_diversity, 0) AS category_diversity
        
    FROM users u
    LEFT JOIN (
        SELECT user_id, total_income, total_expense, net_savings
        FROM v_income_vs_expense
        WHERE year = EXTRACT(YEAR FROM CURRENT_DATE)
        AND month = EXTRACT(MONTH FROM CURRENT_DATE)
    ) cm ON u.id = cm.user_id
    LEFT JOIN (
        SELECT user_id, ROUND(AVG(LEAST(usage_percentage, 100)), 2) AS avg_budget_adherence
        FROM v_budget_vs_actual
        WHERE year = EXTRACT(YEAR FROM CURRENT_DATE)
        AND month = EXTRACT(MONTH FROM CURRENT_DATE)
        GROUP BY user_id
    ) ba ON u.id = ba.user_id
    LEFT JOIN (
        SELECT user_id, SUM(balance) AS total_balance
        FROM wallets WHERE is_active = TRUE
        GROUP BY user_id
    ) wb ON u.id = wb.user_id
    LEFT JOIN (
        SELECT user_id, COUNT(DISTINCT category_id) AS category_diversity
        FROM transactions
        WHERE transaction_date >= DATE_TRUNC('month', CURRENT_DATE)
        GROUP BY user_id
    ) td ON u.id = td.user_id
)
SELECT 
    user_id,
    full_name,
    email,
    current_month_income,
    current_month_expense,
    current_month_savings,
    budget_adherence,
    total_balance,
    category_diversity,
    
    -- Financial Health Score (0-100)
    ROUND(
        -- Savings rate component (40 points max)
        LEAST(CASE 
            WHEN current_month_income > 0 
            THEN (current_month_savings / current_month_income) * 100
            ELSE 0
        END, 40) +
        
        -- Budget adherence component (30 points max)
        LEAST(budget_adherence * 0.3, 30) +
        
        -- Balance component (20 points max)
        LEAST(CASE 
            WHEN total_balance > 0 THEN 20
            WHEN total_balance = 0 THEN 10
            ELSE 0
        END, 20) +
        
        -- Diversity component (10 points max)
        LEAST(category_diversity, 10)
    , 2) AS health_score,
    
    -- Health category
    CASE 
        WHEN current_month_income = 0 AND current_month_expense = 0 THEN 'No Activity'
        WHEN (
            LEAST(CASE WHEN current_month_income > 0 THEN (current_month_savings / current_month_income) * 100 ELSE 0 END, 40) +
            LEAST(budget_adherence * 0.3, 30) +
            LEAST(CASE WHEN total_balance > 0 THEN 20 WHEN total_balance = 0 THEN 10 ELSE 0 END, 20) +
            LEAST(category_diversity, 10)
        ) >= 80 THEN 'Excellent'
        WHEN (
            LEAST(CASE WHEN current_month_income > 0 THEN (current_month_savings / current_month_income) * 100 ELSE 0 END, 40) +
            LEAST(budget_adherence * 0.3, 30) +
            LEAST(CASE WHEN total_balance > 0 THEN 20 WHEN total_balance = 0 THEN 10 ELSE 0 END, 20) +
            LEAST(category_diversity, 10)
        ) >= 60 THEN 'Good'
        WHEN (
            LEAST(CASE WHEN current_month_income > 0 THEN (current_month_savings / current_month_income) * 100 ELSE 0 END, 40) +
            LEAST(budget_adherence * 0.3, 30) +
            LEAST(CASE WHEN total_balance > 0 THEN 20 WHEN total_balance = 0 THEN 10 ELSE 0 END, 20) +
            LEAST(category_diversity, 10)
        ) >= 40 THEN 'Fair'
        ELSE 'Needs Improvement'
    END AS health_category

FROM user_metrics;

-- ============================================
-- 13. EXPENSE FORECAST (Simple Moving Average)
-- ============================================

CREATE OR REPLACE VIEW v_expense_forecast AS
WITH monthly_expenses AS (
    SELECT 
        user_id,
        EXTRACT(YEAR FROM transaction_date)::INTEGER AS year,
        EXTRACT(MONTH FROM transaction_date)::INTEGER AS month,
        SUM(amount) AS total_expense
    FROM transactions
    WHERE type = 'expense'
    GROUP BY user_id, EXTRACT(YEAR FROM transaction_date), EXTRACT(MONTH FROM transaction_date)
)
SELECT 
    user_id,
    year,
    month,
    total_expense,
    
    -- 3-month moving average
    ROUND(AVG(total_expense) OVER (
        PARTITION BY user_id ORDER BY year, month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS ma_3_month,
    
    -- 6-month moving average (for next month forecast)
    ROUND(AVG(total_expense) OVER (
        PARTITION BY user_id ORDER BY year, month
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ), 2) AS ma_6_month,
    
    -- Trend (increasing/decreasing)
    CASE 
        WHEN total_expense > LAG(total_expense) OVER (PARTITION BY user_id ORDER BY year, month)
        THEN 'Increasing'
        WHEN total_expense < LAG(total_expense) OVER (PARTITION BY user_id ORDER BY year, month)
        THEN 'Decreasing'
        ELSE 'Stable'
    END AS expense_trend,
    
    -- Volatility (standard deviation over 3 months)
    ROUND(STDDEV(total_expense) OVER (
        PARTITION BY user_id ORDER BY year, month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS expense_volatility

FROM monthly_expenses
ORDER BY user_id, year, month;

-- ============================================
-- 14. KPI SUMMARY VIEW (For Dashboard Cards)
-- ============================================

CREATE OR REPLACE VIEW v_kpi_summary AS
SELECT 
    u.id AS user_id,
    u.full_name,
    
    -- Current Month KPIs
    COALESCE(cm.total_income, 0) AS mtd_income,
    COALESCE(cm.total_expense, 0) AS mtd_expense,
    COALESCE(cm.net_savings, 0) AS mtd_savings,
    COALESCE(cm.expense_ratio, 0) AS mtd_expense_ratio,
    
    -- Transaction counts
    COALESCE(tc.transaction_count, 0) AS mtd_transactions,
    
    -- Budget KPIs
    COALESCE(bk.budgets_on_track, 0) AS budgets_on_track,
    COALESCE(bk.budgets_exceeded, 0) AS budgets_exceeded,
    COALESCE(bk.total_budgets, 0) AS total_budgets,
    
    -- Wallet KPIs
    COALESCE(wk.total_balance, 0) AS total_balance,
    COALESCE(wk.active_wallets, 0) AS active_wallets,
    
    -- Comparison with last month
    COALESCE(lm.total_income, 0) AS last_month_income,
    COALESCE(lm.total_expense, 0) AS last_month_expense,
    
    -- Change percentages
    CASE 
        WHEN COALESCE(lm.total_income, 0) > 0 
        THEN ROUND((COALESCE(cm.total_income, 0) - lm.total_income) * 100.0 / lm.total_income, 2)
        ELSE 0
    END AS income_change_pct,
    
    CASE 
        WHEN COALESCE(lm.total_expense, 0) > 0 
        THEN ROUND((COALESCE(cm.total_expense, 0) - lm.total_expense) * 100.0 / lm.total_expense, 2)
        ELSE 0
    END AS expense_change_pct

FROM users u
LEFT JOIN (
    SELECT user_id, total_income, total_expense, net_savings, expense_ratio
    FROM v_income_vs_expense
    WHERE year = EXTRACT(YEAR FROM CURRENT_DATE)
    AND month = EXTRACT(MONTH FROM CURRENT_DATE)
) cm ON u.id = cm.user_id
LEFT JOIN (
    SELECT user_id, total_income, total_expense
    FROM v_income_vs_expense
    WHERE year = EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 month')
    AND month = EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')
) lm ON u.id = lm.user_id
LEFT JOIN (
    SELECT user_id, COUNT(*) AS transaction_count
    FROM transactions
    WHERE transaction_date >= DATE_TRUNC('month', CURRENT_DATE)
    GROUP BY user_id
) tc ON u.id = tc.user_id
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(*) FILTER (WHERE usage_percentage < 100) AS budgets_on_track,
        COUNT(*) FILTER (WHERE usage_percentage >= 100) AS budgets_exceeded,
        COUNT(*) AS total_budgets
    FROM v_budget_vs_actual
    WHERE year = EXTRACT(YEAR FROM CURRENT_DATE)
    AND month = EXTRACT(MONTH FROM CURRENT_DATE)
    GROUP BY user_id
) bk ON u.id = bk.user_id
LEFT JOIN (
    SELECT user_id, SUM(balance) AS total_balance, COUNT(*) AS active_wallets
    FROM wallets WHERE is_active = TRUE
    GROUP BY user_id
) wk ON u.id = wk.user_id;

-- ============================================
-- 15. TRANSACTION COMPARISON VIEW (YoY, MoM)
-- ============================================

CREATE OR REPLACE VIEW v_transaction_comparison AS
SELECT 
    t.user_id,
    t.type,
    EXTRACT(YEAR FROM t.transaction_date)::INTEGER AS year,
    EXTRACT(MONTH FROM t.transaction_date)::INTEGER AS month,
    TO_CHAR(t.transaction_date, 'YYYY-MM') AS period,
    COUNT(*) AS transaction_count,
    SUM(t.amount) AS total_amount,
    AVG(t.amount) AS avg_amount,
    
    -- Previous period data
    LAG(SUM(t.amount)) OVER (PARTITION BY t.user_id, t.type, EXTRACT(MONTH FROM t.transaction_date) ORDER BY EXTRACT(YEAR FROM t.transaction_date)) AS same_month_last_year,
    LAG(SUM(t.amount)) OVER (PARTITION BY t.user_id, t.type ORDER BY EXTRACT(YEAR FROM t.transaction_date), EXTRACT(MONTH FROM t.transaction_date)) AS previous_month,
    
    -- YoY change
    CASE 
        WHEN LAG(SUM(t.amount)) OVER (PARTITION BY t.user_id, t.type, EXTRACT(MONTH FROM t.transaction_date) ORDER BY EXTRACT(YEAR FROM t.transaction_date)) > 0
        THEN ROUND((SUM(t.amount) - LAG(SUM(t.amount)) OVER (PARTITION BY t.user_id, t.type, EXTRACT(MONTH FROM t.transaction_date) ORDER BY EXTRACT(YEAR FROM t.transaction_date))) * 100.0 /
            LAG(SUM(t.amount)) OVER (PARTITION BY t.user_id, t.type, EXTRACT(MONTH FROM t.transaction_date) ORDER BY EXTRACT(YEAR FROM t.transaction_date)), 2)
        ELSE NULL
    END AS yoy_change_pct,
    
    -- MoM change
    CASE 
        WHEN LAG(SUM(t.amount)) OVER (PARTITION BY t.user_id, t.type ORDER BY EXTRACT(YEAR FROM t.transaction_date), EXTRACT(MONTH FROM t.transaction_date)) > 0
        THEN ROUND((SUM(t.amount) - LAG(SUM(t.amount)) OVER (PARTITION BY t.user_id, t.type ORDER BY EXTRACT(YEAR FROM t.transaction_date), EXTRACT(MONTH FROM t.transaction_date))) * 100.0 /
            LAG(SUM(t.amount)) OVER (PARTITION BY t.user_id, t.type ORDER BY EXTRACT(YEAR FROM t.transaction_date), EXTRACT(MONTH FROM t.transaction_date)), 2)
        ELSE NULL
    END AS mom_change_pct

FROM transactions t
GROUP BY t.user_id, t.type, EXTRACT(YEAR FROM t.transaction_date), EXTRACT(MONTH FROM t.transaction_date)
ORDER BY t.user_id, year, month;

-- ============================================
-- Grant permissions to read-only users
-- ============================================

GRANT SELECT ON dim_date TO superset_readonly;
GRANT SELECT ON v_fact_transactions TO superset_readonly;
GRANT SELECT ON v_weekly_trends TO superset_readonly;
GRANT SELECT ON v_spending_by_day_of_week TO superset_readonly;
GRANT SELECT ON v_spending_by_hour TO superset_readonly;
GRANT SELECT ON v_monthly_cashflow TO superset_readonly;
GRANT SELECT ON v_category_growth TO superset_readonly;
GRANT SELECT ON v_top_categories TO superset_readonly;
GRANT SELECT ON v_budget_performance TO superset_readonly;
GRANT SELECT ON v_savings_rate TO superset_readonly;
GRANT SELECT ON v_wallet_analytics TO superset_readonly;
GRANT SELECT ON v_user_financial_health TO superset_readonly;
GRANT SELECT ON v_expense_forecast TO superset_readonly;
GRANT SELECT ON v_kpi_summary TO superset_readonly;
GRANT SELECT ON v_transaction_comparison TO superset_readonly;

GRANT SELECT ON dim_date TO n8n_readonly;
GRANT SELECT ON v_fact_transactions TO n8n_readonly;
GRANT SELECT ON v_weekly_trends TO n8n_readonly;
GRANT SELECT ON v_spending_by_day_of_week TO n8n_readonly;
GRANT SELECT ON v_spending_by_hour TO n8n_readonly;
GRANT SELECT ON v_monthly_cashflow TO n8n_readonly;
GRANT SELECT ON v_category_growth TO n8n_readonly;
GRANT SELECT ON v_top_categories TO n8n_readonly;
GRANT SELECT ON v_budget_performance TO n8n_readonly;
GRANT SELECT ON v_savings_rate TO n8n_readonly;
GRANT SELECT ON v_wallet_analytics TO n8n_readonly;
GRANT SELECT ON v_user_financial_health TO n8n_readonly;
GRANT SELECT ON v_expense_forecast TO n8n_readonly;
GRANT SELECT ON v_kpi_summary TO n8n_readonly;
GRANT SELECT ON v_transaction_comparison TO n8n_readonly;

-- ============================================
-- BI Views Phase 3 Complete!
-- ============================================
