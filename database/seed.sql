-- ============================================
-- Personal Finance BI System - Seed Data
-- ============================================
-- Demo data for testing and development

-- ============================================
-- Demo Users (password: 123456)
-- Password hash for '123456' using bcrypt (generated with passlib)
-- ============================================

INSERT INTO users (email, password_hash, full_name) VALUES
    ('demo@finance.app', '$2b$12$hqITojUr7X4A41Ih/0VJKec9mmAE9Ja290wm7UKCOoDsHTibjz0cS', 'Nguyễn Demo'),
    ('test@finance.app', '$2b$12$hqITojUr7X4A41Ih/0VJKec9mmAE9Ja290wm7UKCOoDsHTibjz0cS', 'Trần Test'),
    ('user@finance.app', '$2b$12$hqITojUr7X4A41Ih/0VJKec9mmAE9Ja290wm7UKCOoDsHTibjz0cS', 'Lê User')
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- Demo Wallets
-- ============================================

INSERT INTO wallets (user_id, name, balance, currency, icon) VALUES
    -- User 1: demo@finance.app
    (1, 'Tiền mặt', 5000000, 'VND', 'wallet'),
    (1, 'Ngân hàng VCB', 25000000, 'VND', 'building'),
    (1, 'Ví MoMo', 1500000, 'VND', 'smartphone'),
    -- User 2: test@finance.app
    (2, 'Cash', 2000000, 'VND', 'wallet'),
    (2, 'Bank Account', 15000000, 'VND', 'building')
ON CONFLICT DO NOTHING;

-- ============================================
-- Demo Transactions (Last 3 months)
-- ============================================

-- Current month transactions for User 1
INSERT INTO transactions (user_id, wallet_id, category_id, type, amount, description, transaction_date) VALUES
    -- Income
    (1, 2, 9, 'income', 15000000, 'Lương tháng này', CURRENT_DATE - INTERVAL '5 days'),
    (1, 2, 10, 'income', 3000000, 'Freelance project', CURRENT_DATE - INTERVAL '10 days'),
    
    -- Expenses - Food & Dining (category_id = 1)
    (1, 1, 1, 'expense', 150000, 'Ăn trưa công ty', CURRENT_DATE - INTERVAL '1 day'),
    (1, 1, 1, 'expense', 85000, 'Cà phê', CURRENT_DATE - INTERVAL '2 days'),
    (1, 1, 1, 'expense', 250000, 'Ăn tối gia đình', CURRENT_DATE - INTERVAL '3 days'),
    (1, 3, 1, 'expense', 120000, 'Grab Food', CURRENT_DATE - INTERVAL '4 days'),
    (1, 1, 1, 'expense', 95000, 'Ăn sáng', CURRENT_DATE - INTERVAL '5 days'),
    (1, 1, 1, 'expense', 180000, 'Đi ăn với bạn', CURRENT_DATE - INTERVAL '6 days'),
    (1, 1, 1, 'expense', 75000, 'Cà phê làm việc', CURRENT_DATE - INTERVAL '7 days'),
    (1, 1, 1, 'expense', 320000, 'Siêu thị mua đồ ăn', CURRENT_DATE - INTERVAL '8 days'),
    (1, 3, 1, 'expense', 55000, 'Trà sữa', CURRENT_DATE - INTERVAL '9 days'),
    (1, 1, 1, 'expense', 200000, 'Nhậu cuối tuần', CURRENT_DATE - INTERVAL '10 days'),
    
    -- Expenses - Transportation (category_id = 2)
    (1, 3, 2, 'expense', 150000, 'Grab đi làm', CURRENT_DATE - INTERVAL '1 day'),
    (1, 1, 2, 'expense', 200000, 'Đổ xăng', CURRENT_DATE - INTERVAL '5 days'),
    (1, 3, 2, 'expense', 85000, 'Grab về nhà', CURRENT_DATE - INTERVAL '7 days'),
    (1, 1, 2, 'expense', 50000, 'Gửi xe', CURRENT_DATE - INTERVAL '10 days'),
    
    -- Expenses - Shopping (category_id = 3)
    (1, 2, 3, 'expense', 500000, 'Mua quần áo', CURRENT_DATE - INTERVAL '3 days'),
    (1, 3, 3, 'expense', 350000, 'Mua đồ online', CURRENT_DATE - INTERVAL '8 days'),
    
    -- Expenses - Entertainment (category_id = 4)
    (1, 1, 4, 'expense', 150000, 'Xem phim', CURRENT_DATE - INTERVAL '6 days'),
    (1, 3, 4, 'expense', 200000, 'Netflix + Spotify', CURRENT_DATE - INTERVAL '15 days'),
    
    -- Expenses - Bills (category_id = 5)
    (1, 2, 5, 'expense', 500000, 'Tiền điện', CURRENT_DATE - INTERVAL '10 days'),
    (1, 2, 5, 'expense', 200000, 'Tiền nước', CURRENT_DATE - INTERVAL '10 days'),
    (1, 2, 5, 'expense', 300000, 'Internet', CURRENT_DATE - INTERVAL '12 days'),
    (1, 3, 5, 'expense', 150000, 'Điện thoại', CURRENT_DATE - INTERVAL '15 days')
ON CONFLICT DO NOTHING;

-- Last month transactions for User 1
INSERT INTO transactions (user_id, wallet_id, category_id, type, amount, description, transaction_date) VALUES
    -- Income
    (1, 2, 9, 'income', 14500000, 'Lương tháng trước', CURRENT_DATE - INTERVAL '35 days'),
    (1, 2, 12, 'income', 500000, 'Quà sinh nhật', CURRENT_DATE - INTERVAL '40 days'),
    
    -- Expenses
    (1, 1, 1, 'expense', 1800000, 'Ăn uống tháng trước', CURRENT_DATE - INTERVAL '32 days'),
    (1, 1, 2, 'expense', 450000, 'Di chuyển', CURRENT_DATE - INTERVAL '35 days'),
    (1, 2, 3, 'expense', 1200000, 'Mua sắm', CURRENT_DATE - INTERVAL '38 days'),
    (1, 2, 5, 'expense', 1100000, 'Hóa đơn các loại', CURRENT_DATE - INTERVAL '40 days'),
    (1, 1, 4, 'expense', 400000, 'Giải trí', CURRENT_DATE - INTERVAL '42 days'),
    (1, 2, 6, 'expense', 500000, 'Khám bệnh', CURRENT_DATE - INTERVAL '45 days')
ON CONFLICT DO NOTHING;

-- 2 months ago transactions for User 1
INSERT INTO transactions (user_id, wallet_id, category_id, type, amount, description, transaction_date) VALUES
    (1, 2, 9, 'income', 14000000, 'Lương', CURRENT_DATE - INTERVAL '65 days'),
    (1, 2, 10, 'income', 2000000, 'Thưởng dự án', CURRENT_DATE - INTERVAL '70 days'),
    (1, 1, 1, 'expense', 2200000, 'Ăn uống', CURRENT_DATE - INTERVAL '62 days'),
    (1, 1, 2, 'expense', 600000, 'Di chuyển', CURRENT_DATE - INTERVAL '65 days'),
    (1, 2, 3, 'expense', 800000, 'Mua sắm', CURRENT_DATE - INTERVAL '68 days'),
    (1, 2, 5, 'expense', 1050000, 'Hóa đơn', CURRENT_DATE - INTERVAL '70 days')
ON CONFLICT DO NOTHING;

-- ============================================
-- Demo Budgets (Current month)
-- ============================================

INSERT INTO budgets (user_id, category_id, amount, month, year) VALUES
    (1, 1, 2500000, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER),  -- Food
    (1, 2, 800000, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER),   -- Transportation
    (1, 3, 1500000, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER),  -- Shopping
    (1, 4, 500000, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER),   -- Entertainment
    (1, 5, 1500000, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER)   -- Bills
ON CONFLICT DO NOTHING;

-- Transactions for User 2
INSERT INTO transactions (user_id, wallet_id, category_id, type, amount, description, transaction_date) VALUES
    (2, 5, 9, 'income', 12000000, 'Monthly Salary', CURRENT_DATE - INTERVAL '5 days'),
    (2, 4, 1, 'expense', 500000, 'Groceries', CURRENT_DATE - INTERVAL '2 days'),
    (2, 4, 2, 'expense', 200000, 'Gas', CURRENT_DATE - INTERVAL '4 days'),
    (2, 5, 5, 'expense', 800000, 'Bills', CURRENT_DATE - INTERVAL '10 days')
ON CONFLICT DO NOTHING;

-- ============================================
-- Seed data complete!
-- ============================================
-- Demo accounts:
--   Email: demo@finance.app  Password: 123456
--   Email: test@finance.app  Password: 123456
--   Email: user@finance.app  Password: 123456
-- ============================================
