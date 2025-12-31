-- SPiTAK Ecosystem Database Schema

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    username VARCHAR(50) UNIQUE,
    wallet_address TEXT UNIQUE,
    referral_code VARCHAR(10) UNIQUE,
    referred_by UUID,
    is_kyc_verified BOOLEAN DEFAULT false,
    kyc_tier INT DEFAULT 0,
    balance_steps INT DEFAULT 0,
    balance_spitak DECIMAL(18, 2) DEFAULT 0.0,
    total_earned DECIMAL(18, 2) DEFAULT 0.0,
    streak_days INT DEFAULT 0,
    last_activity_date DATE,
    district VARCHAR(50),
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица транзакций
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    type VARCHAR(20) NOT NULL,
    amount DECIMAL(18, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'SPITAK',
    status VARCHAR(15) DEFAULT 'pending',
    description TEXT,
    bank_tx_id TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица ваучеров/купонов
CREATE TABLE IF NOT EXISTS vouchers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_name VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    discount_value VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price_spitak DECIMAL(10, 2) NOT NULL,
    image_url TEXT,
    emoji VARCHAR(10),
    terms TEXT,
    valid_until DATE,
    total_quantity INT,
    remaining_quantity INT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица покупок ваучеров
CREATE TABLE IF NOT EXISTS voucher_purchases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    voucher_id UUID NOT NULL,
    transaction_id UUID,
    qr_code TEXT,
    redemption_code VARCHAR(50) UNIQUE,
    is_redeemed BOOLEAN DEFAULT false,
    redeemed_at TIMESTAMP,
    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица шагов (дневная статистика)
CREATE TABLE IF NOT EXISTS daily_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    date DATE NOT NULL,
    steps_count INT NOT NULL DEFAULT 0,
    distance_km DECIMAL(10, 2) DEFAULT 0.0,
    calories_burned INT DEFAULT 0,
    active_minutes INT DEFAULT 0,
    spitak_earned DECIMAL(10, 2) DEFAULT 0.0,
    boost_multiplier DECIMAL(3, 2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

-- Таблица районов (для битвы районов)
CREATE TABLE IF NOT EXISTS districts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    city VARCHAR(50) DEFAULT 'Yerevan',
    total_steps BIGINT DEFAULT 0,
    active_users INT DEFAULT 0,
    rank INT,
    emoji VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица стейкинга
CREATE TABLE IF NOT EXISTS staking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    amount DECIMAL(18, 2) NOT NULL,
    multiplier DECIMAL(3, 2) DEFAULT 1.2,
    staked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unlock_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Таблица рефералов
CREATE TABLE IF NOT EXISTS referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_id UUID NOT NULL,
    referred_user_id UUID NOT NULL,
    bonus_spitak DECIMAL(10, 2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);
CREATE INDEX IF NOT EXISTS idx_users_wallet ON users(wallet_address);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_daily_steps_user_date ON daily_steps(user_id, date);
CREATE INDEX IF NOT EXISTS idx_voucher_purchases_user ON voucher_purchases(user_id);
CREATE INDEX IF NOT EXISTS idx_voucher_purchases_voucher ON voucher_purchases(voucher_id);