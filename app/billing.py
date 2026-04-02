from __future__ import annotations

from app import db


CURRENCY_MAP = {
    "Россия": ("RUB", "₽"),
    "Казахстан": ("KZT", "₸"),
    "Украина": ("UAH", "₴"),
    "Другое": ("USD", "$"),
    "Other": ("USD", "$"),
}
DEFAULT_CURRENCY = ("USD", "$")


def get_currency(country: str | None) -> tuple[str, str]:
    return CURRENCY_MAP.get(country or "", DEFAULT_CURRENCY)


def _settings_float(bs, key: str, default: float = 0.0) -> float:
    try:
        v = bs[key]
        return float(v) if v is not None else default
    except (KeyError, TypeError):
        return default


def signup_referral_bonus(bs, kind: str, country: str | None) -> float:
    """Бонус за регистрацию по реф-ссылке.

    ``kind``: ``referral_bonus`` — пригласившему, ``reffer_bonus`` — новому пользователю.
    Берётся колонка ``{kind}_{kzt|rub|uah|usd}`` по стране.
    """
    suffix = {"Казахстан": "kzt", "Россия": "rub", "Украина": "uah"}.get(country or "", "usd")
    return _settings_float(bs, f"{kind}_{suffix}", 0.0)


def topup_referrer_reward_percent(bs) -> float:
    """Процент вознаграждения реферера с пополнения реферала (``referral_reward_percent``)."""
    return _settings_float(bs, "referral_reward_percent", 0.0)


async def get_exchange_rate(country: str | None) -> float:
    bs = await db.get_bot_settings()
    if country == "Россия":
        return float(bs["currency_usd_rub"])
    elif country == "Казахстан":
        return float(bs["currency_usd_kzt"])
    elif country == "Украина":
        return float(bs["currency_usd_uah"])
    return 1.0


async def markup_multiplier() -> float:
    """1 + markup_percent/100 — множитель к базовой стоимости в USD."""
    bs = await db.get_bot_settings()
    pct = float(bs.get("markup_percent") or 0)
    return 1.0 + max(0.0, pct) / 100.0


async def with_markup_usd(base_usd: float) -> float:
    if base_usd <= 0:
        return 0.0
    return base_usd * await markup_multiplier()


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
    billed_usd = await with_markup_usd(cost_usd)
    cost_local = round(billed_usd * rate, 4)
    new_balance = await db.deduct_balance(user_id, cost_local)
    return cost_local, new_balance


async def check_balance(user_id: int, estimated_cost_usd: float, country: str | None) -> bool:
    rate = await get_exchange_rate(country)
    balance = await db.get_balance(user_id)
    need_usd = await with_markup_usd(estimated_cost_usd)
    return balance >= need_usd * rate


async def charge_whisper(user_id: int, duration_sec: float, country: str | None) -> tuple[float, float]:
    bs = await db.get_bot_settings()
    cost_usd = (duration_sec / 60) * float(bs["price_whisper"])
    return await charge_user(user_id, cost_usd, country)


async def charge_tts(user_id: int, char_count: int, country: str | None) -> tuple[float, float]:
    bs = await db.get_bot_settings()
    cost_usd = (char_count / 1000) * float(bs["price_tts"])
    return await charge_user(user_id, cost_usd, country)


async def charge_image(user_id: int, country: str | None) -> tuple[float, float]:
    bs = await db.get_bot_settings()
    cost_usd = float(bs["price_image"])
    return await charge_user(user_id, cost_usd, country)


def _fmt_rate_usd(n: float) -> str:
    x = float(n)
    if x >= 100:
        return f"{x:.2f}".rstrip("0").rstrip(".")
    if x >= 1:
        return f"{x:.3f}".rstrip("0").rstrip(".")
    return f"{x:.5f}".rstrip("0").rstrip(".")


async def format_prices_markdown(lang: str) -> str:
    """Тарифы для пользователя: из bot_settings × наценка (как реально списывается)."""
    from app.locales import t

    bs = await db.get_bot_settings()
    mult = await markup_multiplier()

    prem_in = 1000 * float(bs["price_input_premium"]) * mult
    prem_out = 1000 * float(bs["price_output_premium"]) * mult
    mini_in = 1000 * float(bs["price_input"]) * mult
    mini_out = 1000 * float(bs["price_output"]) * mult
    whisper = float(bs["price_whisper"]) * mult
    tts = 1000 * float(bs["price_tts"]) * mult
    image = float(bs["price_image"]) * mult

    return t(
        "prices_dynamic", lang,
        prem_in=_fmt_rate_usd(prem_in),
        prem_out=_fmt_rate_usd(prem_out),
        mini_in=_fmt_rate_usd(mini_in),
        mini_out=_fmt_rate_usd(mini_out),
        whisper=_fmt_rate_usd(whisper),
        tts=_fmt_rate_usd(tts),
        image=_fmt_rate_usd(image),
    )
