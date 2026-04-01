from __future__ import annotations

import logging

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app import db
from app.billing import get_currency, get_exchange_rate
from app.keyboards import (
    language_keyboard, country_keyboard, terms_keyboard, welcome_keyboard,
)
from app.locales import t

log = logging.getLogger(__name__)
router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, db_user=None, lang: str = "en"):
    referrer = 0
    if message.text and " " in message.text:
        try:
            referrer = int(message.text.split(" ", 1)[1])
        except (ValueError, IndexError):
            pass

    if db_user is None:
        user = message.from_user
        await db.create_user(
            user_id=user.id,
            name=user.first_name,
            surname=user.last_name,
            username=user.username,
            referrer=referrer,
        )
        if referrer:
            bs = await db.get_bot_settings()
            bonus = float(bs["referral_bonus"])
            if bonus > 0:
                await db.add_balance(referrer, bonus)
                await db.create_transaction(
                    referrer, 2, bonus, "USD",
                    description="Referral bonus", referral_id=user.id,
                )
            reffer_bonus = float(bs["reffer_bonus"])
            if reffer_bonus > 0:
                await db.add_balance(user.id, reffer_bonus)
                await db.create_transaction(
                    user.id, 2, reffer_bonus, "USD",
                    description="Welcome referral bonus",
                )

        await message.answer(
            t("choose_language", "en"),
            reply_markup=language_keyboard(),
        )
    else:
        await message.answer(
            t("welcome_message", lang),
            parse_mode="Markdown",
            reply_markup=welcome_keyboard(lang),
        )


@router.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery, db_user=None):
    lang = callback.data.split(":")[1]
    user_id = callback.from_user.id

    await db.update_user(user_id, language=lang)

    user = await db.get_user(user_id)
    if user and user["country"]:
        await callback.message.edit_text(
            t("welcome_message", lang),
            parse_mode="Markdown",
            reply_markup=welcome_keyboard(lang),
        )
    else:
        await callback.message.edit_text(
            t("choose_country", lang),
            reply_markup=country_keyboard(lang),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("country:"))
async def set_country(callback: CallbackQuery, lang: str = "en"):
    new_country = callback.data.split(":")[1]
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    old_country = user["country"] if user else None

    if old_country and old_country != new_country:
        await _convert_balance(user_id, old_country, new_country)

    await db.update_user(user_id, country=new_country)

    user = await db.get_user(user_id)
    if user and not user["terms_of_use"]:
        await callback.message.edit_text(
            t("terms_of_use", lang),
            parse_mode="Markdown",
            reply_markup=terms_keyboard(lang),
        )
    else:
        if old_country and old_country != new_country:
            await callback.message.edit_text(
                t("country_changed", lang),
                reply_markup=welcome_keyboard(lang),
            )
        else:
            await callback.message.edit_text(
                t("welcome_message", lang),
                parse_mode="Markdown",
                reply_markup=welcome_keyboard(lang),
            )
    await callback.answer()


async def _convert_balance(user_id: int, old_country: str, new_country: str):
    """Convert user balance from old country currency to new country currency."""
    try:
        from aiohttp import ClientSession

        old_cur_code, _ = get_currency(old_country)
        new_cur_code, _ = get_currency(new_country)

        if old_cur_code == new_cur_code:
            return

        balance = await db.get_balance(user_id)
        if balance <= 0:
            return

        async with ClientSession() as session:
            async with session.get(f"https://api.exchangerate-api.com/v4/latest/{old_cur_code}") as resp:
                data = await resp.json()
                rate = data["rates"].get(new_cur_code, 1.0)

        new_balance = round(balance * rate * 0.98, 2)
        await db.set_balance(user_id, new_balance)

        await db.create_transaction(
            user_id, 4, balance, old_cur_code,
            description="Currency conversion (withdrawal)",
        )
        await db.create_transaction(
            user_id, 5, new_balance, new_cur_code,
            description="Currency conversion (credit)",
        )
    except Exception as e:
        log.error("Balance conversion error: %s", e)


@router.callback_query(F.data == "accept_terms")
async def accept_terms(callback: CallbackQuery, lang: str = "en"):
    await db.update_user(callback.from_user.id, terms_of_use=True)
    await callback.message.edit_text(
        t("welcome_message", lang),
        parse_mode="Markdown",
        reply_markup=welcome_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "welcome")
async def welcome_menu(callback: CallbackQuery, lang: str = "en"):
    await callback.message.edit_text(
        t("welcome_message", lang),
        parse_mode="Markdown",
        reply_markup=welcome_keyboard(lang),
    )
    await callback.answer()
