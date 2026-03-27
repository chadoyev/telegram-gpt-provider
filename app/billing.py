from __future__ import annotations

from app import db


CURRENCY_MAP = {
    "Россия": ("RUB", "₽"),
    "Казахстан": ("KZT", "₸"),
    "Украина": ("UAH", "₴"),
}
DEFAULT_CURRENCY = ("USD", "$")


def get_currency(country: str | None) -> tuple[str, str]:
    return CURRENCY_MAP.get(country or "", DEFAULT_CURRENCY)


async def get_exchange_rate(country: str | None) -> float:
    bs = await db.get_bot_settings()
    if country == "Россия":
        return float(bs["currency_usd_rub"])
    elif country == "Казахстан":
        return float(bs["currency_usd_kzt"])
    elif country == "Украина":
        return float(bs["currency_usd_uah"])
    return 1.0


async def calculate_cost_usd(
    input_tokens: int, output_tokens: int, model: str,
) -> float:
    bs = await db.get_bot_settings()
    if model.endswith("-mini"):
        price_in = float(bs["price_input"])
        price_out = float(bs["price_output"])
    else:
        price_in = float(bs["price_input_premium"])
        price_out = float(bs["price_output_premium"])
    return (input_tokens / 1000) * price_in + (output_tokens / 1000) * price_out


async def charge_user(
    user_id: int, cost_usd: float, country: str | None,
) -> tuple[float, float]:
    """Deduct from user balance. Returns (cost_local, new_balance)."""
    rate = await get_exchange_rate(country)
    cost_local = round(cost_usd * rate, 4)
    new_balance = await db.deduct_balance(user_id, cost_local)
    return cost_local, new_balance


async def check_balance(user_id: int, estimated_cost_usd: float, country: str | None) -> bool:
    rate = await get_exchange_rate(country)
    balance = await db.get_balance(user_id)
    return balance >= estimated_cost_usd * rate


async def charge_whisper(user_id: int, duration_sec: float, country: str | None) -> tuple[float, float]:
    bs = await db.get_bot_settings()
    cost_usd = (duration_sec / 60) * float(bs["price_whisper"])
    return await charge_user(user_id, cost_usd, country)


async def charge_tts(user_id: int, char_count: int, country: str | None) -> tuple[float, float]:
    bs = await db.get_bot_settings()
    cost_usd = (char_count / 1000) * float(bs["price_tts"])
    return await charge_user(user_id, cost_usd, country)


async def charge_dalle(user_id: int, country: str | None) -> tuple[float, float]:
    bs = await db.get_bot_settings()
    cost_usd = float(bs["price_dalle"])
    return await charge_user(user_id, cost_usd, country)
