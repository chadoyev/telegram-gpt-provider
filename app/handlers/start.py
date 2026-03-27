from __future__ import annotations

import logging

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app import db
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
                await db.add_balance(user.id, float(bs["reffer_bonus"]))

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
    lang_name_map = {"ru": "Русский", "kz": "Казахский", "ua": "Украинский", "en": "Английский"}
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
    country = callback.data.split(":")[1]
    user_id = callback.from_user.id
    await db.update_user(user_id, country=country)

    user = await db.get_user(user_id)
    if user and not user["terms_of_use"]:
        await callback.message.edit_text(
            t("terms_of_use", lang),
            parse_mode="Markdown",
            reply_markup=terms_keyboard(lang),
        )
    else:
        await callback.message.edit_text(
            t("welcome_message", lang),
            parse_mode="Markdown",
            reply_markup=welcome_keyboard(lang),
        )
    await callback.answer()


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
