-- UAI Robot — PostgreSQL schema
-- This file is for reference. The bot auto-creates tables on startup.
-- To initialize manually: psql -U postgres -d uai_robot -f schema.sql

CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT UNIQUE NOT NULL,
    user_name       TEXT NOT NULL,
    user_surname    TEXT,
    username        TEXT,
    date_reg        TIMESTAMPTZ NOT NULL DEFAULT now(),
    terms_of_use    BOOLEAN DEFAULT FALSE,
    status_chat     BOOLEAN DEFAULT FALSE,
    reffer          BIGINT DEFAULT 0,
    balance         NUMERIC(12,4) DEFAULT 0,
    language        TEXT DEFAULT NULL,
    country         TEXT DEFAULT NULL,
    ai_model        TEXT DEFAULT 'gpt-5.4-mini',
    ai_voice        TEXT DEFAULT 'nova',
    voice_enabled   BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS chat_history (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    chat_id         INTEGER NOT NULL,
    role            TEXT NOT NULL,
    content         TEXT,
    file_type       TEXT,
    file_path       TEXT,
    spending        TEXT,
    model           TEXT,
    created_at      TIMESTAMPTZ DEFAULT now(),
    status_closed   BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS transactions (
    id                  SERIAL PRIMARY KEY,
    user_id             BIGINT NOT NULL,
    type                INTEGER NOT NULL,
    merchant_order_id   TEXT UNIQUE,
    amount              NUMERIC(12,4) NOT NULL,
    currency            TEXT NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    status              BOOLEAN DEFAULT FALSE,
    description         TEXT,
    referral_id         BIGINT,
    chat_number         INTEGER
);

CREATE TABLE IF NOT EXISTS bot_settings (
    id                   SERIAL PRIMARY KEY,
    status               BOOLEAN DEFAULT TRUE,
    max_tokens           INTEGER DEFAULT 4096,
    temperature          NUMERIC(3,2) DEFAULT 0.70,
    reffer_bonus         NUMERIC(12,4) DEFAULT 0,
    referral_bonus       NUMERIC(12,4) DEFAULT 0,
    cashback             INTEGER DEFAULT 5,
    price_input          NUMERIC(10,6) DEFAULT 0.000900,
    price_output         NUMERIC(10,6) DEFAULT 0.005400,
    price_whisper        NUMERIC(10,6) DEFAULT 0.003600,
    price_tts            NUMERIC(10,6) DEFAULT 0.018000,
    price_image          NUMERIC(10,4) DEFAULT 0.0410,
    price_input_premium  NUMERIC(10,6) DEFAULT 0.003000,
    price_output_premium NUMERIC(10,6) DEFAULT 0.018000,
    currency_usd_rub     NUMERIC(10,2) DEFAULT 95.00,
    currency_usd_kzt     NUMERIC(10,2) DEFAULT 470.00,
    currency_usd_uah     NUMERIC(10,2) DEFAULT 41.00
);

INSERT INTO bot_settings DEFAULT VALUES
ON CONFLICT DO NOTHING;

CREATE INDEX IF NOT EXISTS idx_chat_history_user ON chat_history(user_id, chat_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
