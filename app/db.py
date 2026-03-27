from __future__ import annotations

import asyncpg
import logging
from datetime import datetime
from typing import Any

from app.config import settings

log = logging.getLogger(__name__)

pool: asyncpg.Pool | None = None


async def create_pool() -> asyncpg.Pool:
    global pool
    pool = await asyncpg.create_pool(
        dsn=settings.db.dsn,
        min_size=settings.db.min_pool,
        max_size=settings.db.max_pool,
    )
    log.info("Database pool created (%s–%s)", settings.db.min_pool, settings.db.max_pool)
    return pool


async def close_pool() -> None:
    global pool
    if pool:
        await pool.close()
        pool = None
        log.info("Database pool closed")


async def init_schema() -> None:
    assert pool
    async with pool.acquire() as conn:
        await conn.execute("""
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
        """)
        await conn.execute("""
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
        """)
        await conn.execute("""
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
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS bot_settings (
            id              SERIAL PRIMARY KEY,
            status          BOOLEAN DEFAULT TRUE,
            max_tokens      INTEGER DEFAULT 4096,
            temperature     NUMERIC(3,2) DEFAULT 0.7,
            reffer_bonus    NUMERIC(12,4) DEFAULT 0,
            referral_bonus  NUMERIC(12,4) DEFAULT 0,
            cashback        INTEGER DEFAULT 5,
            price_input     NUMERIC(10,6) DEFAULT 0.000900,
            price_output    NUMERIC(10,6) DEFAULT 0.005400,
            price_whisper   NUMERIC(10,6) DEFAULT 0.007200,
            price_tts       NUMERIC(10,6) DEFAULT 0.018000,
            price_dalle     NUMERIC(10,4) DEFAULT 0.0480,
            price_input_premium  NUMERIC(10,6) DEFAULT 0.003000,
            price_output_premium NUMERIC(10,6) DEFAULT 0.018000,
            currency_usd_rub NUMERIC(10,2) DEFAULT 95.0,
            currency_usd_kzt NUMERIC(10,2) DEFAULT 470.0,
            currency_usd_uah NUMERIC(10,2) DEFAULT 41.0
        );
        """)
        count = await conn.fetchval("SELECT count(*) FROM bot_settings")
        if count == 0:
            await conn.execute("INSERT INTO bot_settings DEFAULT VALUES")
    log.info("Database schema initialized")


# ── User queries ─────────────────────────────────────────────────

async def get_user(user_id: int) -> asyncpg.Record | None:
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)


async def create_user(
    user_id: int, name: str, surname: str | None,
    username: str | None, referrer: int = 0,
) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO users (user_id, user_name, user_surname, username, reffer)
               VALUES ($1, $2, $3, $4, $5) ON CONFLICT (user_id) DO NOTHING""",
            user_id, name, surname or "", username or "", referrer,
        )


async def update_user(user_id: int, **fields: Any) -> None:
    if not fields:
        return
    sets = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(fields))
    vals = [user_id, *fields.values()]
    async with pool.acquire() as conn:
        await conn.execute(f"UPDATE users SET {sets} WHERE user_id = $1", *vals)


async def get_balance(user_id: int) -> float:
    async with pool.acquire() as conn:
        row = await conn.fetchval("SELECT balance FROM users WHERE user_id = $1", user_id)
        return float(row or 0)


async def deduct_balance(user_id: int, amount: float) -> float:
    async with pool.acquire() as conn:
        new_bal = await conn.fetchval(
            "UPDATE users SET balance = balance - $2 WHERE user_id = $1 RETURNING balance",
            user_id, amount,
        )
        return float(new_bal)


async def add_balance(user_id: int, amount: float) -> float:
    async with pool.acquire() as conn:
        new_bal = await conn.fetchval(
            "UPDATE users SET balance = balance + $2 WHERE user_id = $1 RETURNING balance",
            user_id, amount,
        )
        return float(new_bal)


# ── Chat history ─────────────────────────────────────────────────

async def get_current_chat_id(user_id: int) -> int:
    async with pool.acquire() as conn:
        row = await conn.fetchval(
            "SELECT MAX(chat_id) FROM chat_history WHERE user_id = $1 AND NOT status_closed",
            user_id,
        )
        return row or 0


async def get_next_chat_id(user_id: int) -> int:
    async with pool.acquire() as conn:
        row = await conn.fetchval(
            "SELECT COALESCE(MAX(chat_id), 0) + 1 FROM chat_history WHERE user_id = $1",
            user_id,
        )
        return row or 1


async def save_message(
    user_id: int, chat_id: int, role: str, content: str,
    model: str = "", spending: str = "", file_type: str | None = None,
    file_path: str | None = None,
) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO chat_history
               (user_id, chat_id, role, content, model, spending, file_type, file_path)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
            user_id, chat_id, role, content, model, spending, file_type, file_path,
        )


async def close_chat(user_id: int, chat_id: int) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE chat_history SET status_closed = TRUE WHERE user_id = $1 AND chat_id = $2",
            user_id, chat_id,
        )


async def get_chat_messages(user_id: int, chat_id: int) -> list[asyncpg.Record]:
    async with pool.acquire() as conn:
        return await conn.fetch(
            """SELECT role, content, file_type, file_path, spending, model, created_at
               FROM chat_history WHERE user_id = $1 AND chat_id = $2
               ORDER BY created_at""",
            user_id, chat_id,
        )


async def get_all_chat_ids(user_id: int, closed_only: bool = True) -> list[int]:
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT DISTINCT chat_id FROM chat_history
               WHERE user_id = $1 AND ($2 = FALSE OR status_closed = TRUE)
               ORDER BY chat_id""",
            user_id, closed_only,
        )
        return [r["chat_id"] for r in rows]


async def delete_user_history(user_id: int) -> None:
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM chat_history WHERE user_id = $1", user_id)


# ── Transactions ─────────────────────────────────────────────────

async def create_transaction(
    user_id: int, tx_type: int, amount: float, currency: str,
    merchant_order_id: str | None = None, description: str | None = None,
    referral_id: int | None = None, chat_number: int | None = None,
) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO transactions
               (user_id, type, merchant_order_id, amount, currency, status, description, referral_id, chat_number)
               VALUES ($1, $2, $3, $4, $5, TRUE, $6, $7, $8)""",
            user_id, tx_type, merchant_order_id, amount, currency, description, referral_id, chat_number,
        )


async def get_user_transactions(user_id: int) -> list[asyncpg.Record]:
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM transactions WHERE user_id = $1 ORDER BY created_at DESC",
            user_id,
        )


# ── Bot settings ─────────────────────────────────────────────────

async def get_bot_settings() -> asyncpg.Record:
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM bot_settings LIMIT 1")


async def update_bot_settings(**fields: Any) -> None:
    if not fields:
        return
    sets = ", ".join(f"{k} = ${i+1}" for i, k in enumerate(fields))
    async with pool.acquire() as conn:
        await conn.execute(f"UPDATE bot_settings SET {sets}", *fields.values())


# ── Stats ────────────────────────────────────────────────────────

async def count_users() -> int:
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT count(*) FROM users")


async def count_referrals(user_id: int) -> int:
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT count(*) FROM users WHERE reffer = $1", user_id)


async def count_messages(user_id: int) -> int:
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT count(*) FROM chat_history WHERE user_id = $1 AND role = 'assistant'",
            user_id,
        )


async def count_chats(user_id: int) -> int:
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT count(DISTINCT chat_id) FROM chat_history WHERE user_id = $1",
            user_id,
        )
