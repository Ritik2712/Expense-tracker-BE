-- =========================
-- USERS
-- =========================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_name
ON users(name);


-- =========================
-- ACCOUNTS
-- =========================

CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    balance NUMERIC(12,2) NOT NULL DEFAULT 0,
    user_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_accounts_user_id
ON accounts(user_id);


-- =========================
-- TRANSACTIONS
-- =========================

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    description TEXT,
    amount NUMERIC(12,2) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL,
    account_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (account_id)
        REFERENCES accounts(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_transaction_id
ON transactions(id);

CREATE INDEX IF NOT EXISTS idx_transactions_account_id
ON transactions(account_id);

ALTER TABLE users
ADD CONSTRAINT users_role_check
CHECK (role IN ('user', 'admin'));
