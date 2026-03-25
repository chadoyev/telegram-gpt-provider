-- UAI Robot — PostgreSQL schema
-- Run this file to initialize the database:
--   psql -U postgres -d your_db_name -f schema.sql

CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT UNIQUE NOT NULL,
    user_name       VARCHAR(255) NOT NULL,
    user_surname    VARCHAR(255),
    username        VARCHAR(255),
    date_reg        TIMESTAMP NOT NULL DEFAULT NOW(),
    terms_of_use    BOOLEAN DEFAULT FALSE,
    status_chat     BOOLEAN DEFAULT FALSE,
    reffer          BIGINT DEFAULT 0,
    balance         NUMERIC(12,2) DEFAULT 0,
    balance_bonus   NUMERIC(12,2) DEFAULT 0,
    subscribe_expiration TIMESTAMP DEFAULT NULL,
    language        VARCHAR(50) DEFAULT NULL,
    country         VARCHAR(100) DEFAULT NULL,
    pay             VARCHAR(50) DEFAULT '0',
    status_subscribe BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS history_question_answer (
    user_id         BIGINT NOT NULL,
    id_chat         INTEGER NOT NULL,
    question        TEXT,
    answer          TEXT,
    message_id      VARCHAR(100) NOT NULL,
    date_time       TIMESTAMP,
    status_chat     BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS transactions_history (
    id                  SERIAL PRIMARY KEY,
    user_id             BIGINT NOT NULL,
    type                INTEGER NOT NULL,
    merchant_order_id   VARCHAR(100) UNIQUE,
    amount              NUMERIC(12,2) NOT NULL,
    currency            VARCHAR(10) NOT NULL,
    date_payment        TIMESTAMP NOT NULL,
    status              BOOLEAN DEFAULT FALSE,
    pay_message         VARCHAR(255),
    referal             BIGINT,
    subscription_type   INTEGER
);

CREATE TABLE IF NOT EXISTS settings (
    status          BOOLEAN,
    tokens          INTEGER,
    temperature     NUMERIC(3,2),
    total_blocked   INTEGER,
    reffer_bonus    VARCHAR(100) DEFAULT '0',
    referal_bonus   VARCHAR(100) DEFAULT '0',
    cashback        INTEGER DEFAULT 0,
    pay1            VARCHAR(100) DEFAULT '0',
    pay2            VARCHAR(100) DEFAULT '0',
    pay3            VARCHAR(100) DEFAULT '0',
    pay4            VARCHAR(100) DEFAULT '0',
    subscribe1      VARCHAR(100),
    subscribe2      VARCHAR(100),
    subscribe3      VARCHAR(100),
    subscribe4      VARCHAR(100)
);

-- Default settings row (adjust values as needed)
INSERT INTO settings (status, tokens, temperature, total_blocked,
                      reffer_bonus, referal_bonus, cashback,
                      pay1, pay2, pay3, pay4,
                      subscribe1, subscribe2, subscribe3, subscribe4)
VALUES (TRUE, 1000, 0.1, 0,
        '15-80-8-0.4', '10-60-5-0.25', 5,
        '50-150-35-1', '100-600-50-1.5', '250-1500-115-3.5', '600-3500-280-8',
        '20-115-9-0.5', '100-580-47-1.3', '250-1400-115-3.25', '600-3500-280-7.8');
