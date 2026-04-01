from __future__ import annotations

import hashlib
import logging
import random

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from app import db
from app.billing import get_currency, get_exchange_rate
from app.chat_export import export_transactions
from app.config import settings
from app.keyboards import back_keyboard
from app.locales import t

log = logging.getLogger(__name__)
router = Router(name="payments")


class PayStates(StatesGroup):
    waiting_amount = State()


def _md5(*args) -> str:
    return hashlib.md5(":".join(str(a) for a in args).encode()).hexdigest()


def _robokassa_url(amount, order_info: str, currency: str, desc: str) -> str:
    """Build a Robokassa payment URL.  order_info = 'user_id-inv_id'."""
    parts = order_info.split("-")
    inv_id = parts[1]
    shp_id = f"Shp_id={parts[0]}"
    sign = _md5(settings.robokassa.login, amount, inv_id, currency, settings.robokassa.pass1, shp_id)
    return (
        f"https://auth.robokassa.kz/Merchant/Index.aspx"
        f"?MerchantLogin={settings.robokassa.login}"
        f"&OutSum={amount}&InvoiceID={inv_id}"
        f"&OutSumCurrency={currency}&Description={desc}"
        f"&Shp_id={parts[0]}&SignatureValue={sign}&Encoding=UTF-8"
    )


def _yookassa_payment(amount, currency: str, order_info: str, desc: str) -> str | None:
    """Create a YooKassa payment via SDK. Returns redirect URL or None."""
    try:
        from yookassa import Configuration, Payment
        Configuration.account_id = settings.yookassa.account_id
        Configuration.secret_key = settings.yookassa.secret_key

        parts = order_info.split("-")
        user_id = parts[0]
        order_id = parts[1]

        payment = Payment.create({
            "amount": {"value": str(amount), "currency": currency},
            "confirmation": {
                "type": "redirect",
                "return_url": settings.telegram.bot_url or "https://t.me/uai_robot",
            },
            "capture": True,
            "description": str(desc),
            "metadata": {"order_id": str(order_id), "user_id": str(user_id)},
            "receipt": {
                "customer": {"email": settings.yookassa.receipt_email},
                "items": [{
                    "description": str(desc),
                    "quantity": "1",
                    "amount": {"value": str(amount), "currency": currency},
                    "vat_code": "1",
                }],
            },
        })
        return payment.confirmation.confirmation_url
    except Exception as e:
        log.error("YooKassa payment creation error: %s", e)
        return None


async def _create_payment_link(user_id: int, amount, country: str, lang: str) -> tuple[str | None, str, str, str]:
    """Returns (url, order_id, currency_code, currency_symbol)."""
    inv_id = random.randint(1000, 1_000_000)
    order_id = f"{user_id}-{inv_id}"
    desc = t("pay_description", lang)

    if country == "Россия":
        cur_code, cur_sym = "RUB", "₽"
        if settings.yookassa.account_id:
            url = _yookassa_payment(amount, cur_code, order_id, desc)
        else:
            url = None
    elif country == "Казахстан":
        cur_code, cur_sym = "KZT", "₸"
        url = _robokassa_url(amount, order_id, cur_code, desc)
    elif country == "Украина":
        cur_code, cur_sym = "UAH", "₴"
        rate = await get_exchange_rate("Украина")
        usd_rate_uah = rate
        if usd_rate_uah > 0:
            from aiohttp import ClientSession
            try:
                async with ClientSession() as session:
                    async with session.get("https://api.exchangerate-api.com/v4/latest/UAH") as resp:
                        data = await resp.json()
                        uah_to_usd = data["rates"]["USD"]
            except Exception:
                uah_to_usd = 1 / usd_rate_uah if usd_rate_uah else 0.024
            amount_usd = round(float(amount) * uah_to_usd, 1)
        else:
            amount_usd = float(amount)
        url = _robokassa_url(amount_usd, order_id, "USD", desc)
    else:
        cur_code, cur_sym = "USD", "$"
        url = _robokassa_url(amount, order_id, cur_code, desc)

    return url, order_id, cur_code, cur_sym


@router.callback_query(F.data == "top_up")
async def top_up_menu(callback: CallbackQuery, state: FSMContext, lang: str = "en"):
    user = await db.get_user(callback.from_user.id)
    country = user["country"] if user else "Другое"
    await callback.message.edit_text(
        t("pay_prompt", lang),
        parse_mode="Markdown",
        reply_markup=_payment_keyboard(lang, country),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay:"))
async def quick_pay(callback: CallbackQuery, lang: str = "en"):
    amount = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    country = user["country"] if user else "Другое"

    url, order_id, cur_code, cur_sym = await _create_payment_link(user_id, amount, country, lang)

    if not url:
        await callback.message.edit_text(
            t("unexpected_error", lang),
            reply_markup=back_keyboard(lang, "account"),
        )
        await callback.answer()
        return

    await db.create_transaction(
        user_id, 1, float(amount), cur_code,
        merchant_order_id=order_id, status=False,
        description=t("pay_description", lang),
    )

    pay_btn = InlineKeyboardButton(
        text=f"{t('btn_pay', lang)} {amount} {cur_sym}", url=url,
    )
    back_btn = InlineKeyboardButton(text=f"↩ {t('btn_back', lang)}", callback_data="account")
    kb = InlineKeyboardMarkup(inline_keyboard=[[pay_btn], [back_btn]])

    await callback.message.edit_text(
        t("pay_proceed", lang, amount=amount, cur=cur_sym),
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(F.data == "custom_amount")
async def custom_amount_start(callback: CallbackQuery, state: FSMContext, lang: str = "en"):
    await callback.message.edit_text(t("pay_enter_amount", lang))
    await state.set_state(PayStates.waiting_amount)
    await callback.answer()


@router.message(PayStates.waiting_amount)
async def custom_amount_handler(message: Message, state: FSMContext, db_user=None, lang: str = "en"):
    if not db_user:
        await state.clear()
        return
    user_id = message.from_user.id
    country = db_user["country"] or "Другое"

    min_amounts = {"Россия": 10, "Казахстан": 35, "Украина": 35}
    min_amount = min_amounts.get(country, 1)

    try:
        amount = int(message.text)
        if amount < min_amount:
            raise ValueError
    except ValueError:
        await message.answer(t("pay_error_amount", lang))
        await state.clear()
        return

    url, order_id, cur_code, cur_sym = await _create_payment_link(user_id, amount, country, lang)
    if not url:
        await message.answer(t("unexpected_error", lang))
        await state.clear()
        return

    await db.create_transaction(
        user_id, 1, float(amount), cur_code,
        merchant_order_id=order_id, status=False,
        description=t("pay_description", lang),
    )

    pay_btn = InlineKeyboardButton(
        text=f"{t('btn_pay', lang)} {amount} {cur_sym}", url=url,
    )
    back_btn = InlineKeyboardButton(text=f"↩ {t('btn_back', lang)}", callback_data="account")
    kb = InlineKeyboardMarkup(inline_keyboard=[[pay_btn], [back_btn]])

    await message.answer(
        t("pay_proceed", lang, amount=amount, cur=cur_sym),
        reply_markup=kb,
    )
    await state.clear()


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

    status_msg = await callback.message.edit_text(t("collecting_transactions", lang))

    try:
        from aiogram.types import FSInputFile
        file_path = await export_transactions(user_id, lang)
        doc = FSInputFile(file_path)
        await callback.message.answer_document(
            doc,
            caption=t("your_transactions_file", lang),
        )
    except Exception as e:
        log.error("Transaction export error: %s", e)
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


def _payment_keyboard(lang: str, country: str) -> InlineKeyboardMarkup:
    _, cur = get_currency(country)
    presets = {
        "Россия": [100, 250, 500, 1000, 2500],
        "Казахстан": [500, 1000, 2500, 5000, 10000],
        "Украина": [50, 100, 250, 500, 1000],
    }
    amounts = presets.get(country, [5, 10, 25, 50, 100])

    row1 = [InlineKeyboardButton(text=f"{a}{cur}", callback_data=f"pay:{a}") for a in amounts[:3]]
    row2 = [InlineKeyboardButton(text=f"{a}{cur}", callback_data=f"pay:{a}") for a in amounts[3:]]
    row3 = [InlineKeyboardButton(text=f"✏ {t('btn_custom_amount', lang)}", callback_data="custom_amount")]
    row4 = [InlineKeyboardButton(text=f"↩ {t('btn_back', lang)}", callback_data="account")]

    return InlineKeyboardMarkup(inline_keyboard=[row1, row2, row3, row4])
