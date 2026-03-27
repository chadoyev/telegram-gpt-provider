from __future__ import annotations

import hashlib
import logging
import uuid

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app import db
from app.billing import get_currency, get_exchange_rate
from app.config import settings
from app.keyboards import payment_keyboard, back_keyboard, welcome_keyboard
from app.locales import t

log = logging.getLogger(__name__)
router = Router(name="payments")


class PayStates(StatesGroup):
    waiting_amount = State()


@router.callback_query(F.data == "top_up")
async def top_up_menu(callback: CallbackQuery, lang: str = "en"):
    await callback.message.edit_text(
        t("pay_prompt", lang),
        reply_markup=payment_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay:"))
async def quick_pay(callback: CallbackQuery, lang: str = "en"):
    amount_usd = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    country = user["country"] if user else None

    links = await _generate_payment_links(user_id, amount_usd, country, lang)

    text = f"💳 *{t('pay_prompt', lang)}*\n\n"
    for name, url in links.items():
        if url:
            text += f"🔗 [{name}]({url})\n"

    active_links = {k: v for k, v in links.items() if v}
    if not active_links:
        await callback.message.edit_text(
            "No payment methods configured. Contact admin.",
            reply_markup=back_keyboard(lang, "account"),
        )
    else:
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=back_keyboard(lang, "top_up"),
        )
    await callback.answer()


@router.callback_query(F.data == "my_transactions")
async def my_transactions(callback: CallbackQuery, lang: str = "en"):
    user_id = callback.from_user.id
    txs = await db.get_user_transactions(user_id)
    if not txs:
        await callback.message.edit_text(
            "📭 —",
            reply_markup=back_keyboard(lang, "account"),
        )
        await callback.answer()
        return

    lines = []
    for tx in txs[:20]:
        status = "✅" if tx["status"] else "❌"
        lines.append(
            f"{status} {tx['created_at'].strftime('%d.%m.%Y %H:%M')} | "
            f"{tx['amount']} {tx['currency']}"
        )

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=back_keyboard(lang, "account"),
    )
    await callback.answer()


async def _generate_payment_links(
    user_id: int, amount_usd: int, country: str | None, lang: str,
) -> dict[str, str | None]:
    links: dict[str, str | None] = {}

    rate = await get_exchange_rate(country)
    local_amount = round(amount_usd * rate, 2)
    _, cur_symbol = get_currency(country)
    order_id = f"{user_id}_{uuid.uuid4().hex[:8]}"

    if settings.freekassa.merchant_id:
        sign_str = f"{settings.freekassa.merchant_id}:{local_amount}:{settings.freekassa.secret1}:RUB:{order_id}"
        sign = hashlib.md5(sign_str.encode()).hexdigest()
        links["FreeKassa"] = (
            f"https://pay.freekassa.com/?m={settings.freekassa.merchant_id}"
            f"&oa={local_amount}&currency=RUB&o={order_id}&s={sign}"
        )

    if settings.robokassa.login:
        sign_str = f"{settings.robokassa.login}:{local_amount}:{order_id}:{settings.robokassa.pass1}"
        sign = hashlib.md5(sign_str.encode()).hexdigest()
        links["Robokassa"] = (
            f"https://auth.robokassa.ru/Merchant/Index.aspx"
            f"?MerchantLogin={settings.robokassa.login}"
            f"&OutSum={local_amount}&InvId={order_id}&SignatureValue={sign}"
            f"&IsTest=0"
        )

    if settings.yookassa.account_id:
        links["YooKassa"] = None

    return links
