from __future__ import annotations

import logging
from datetime import date

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app import db
from app.billing import get_currency
from app.config import settings, VOICES
from app.keyboards import (
    account_keyboard, model_keyboard, voice_keyboard,
    chats_menu_keyboard, back_keyboard, welcome_keyboard,
)
from app.locales import t

log = logging.getLogger(__name__)
router = Router(name="menu")


@router.callback_query(F.data == "account")
async def show_account(callback: CallbackQuery, lang: str = "en"):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.answer()
        return

    refs = await db.count_referrals(user_id)
    msgs = await db.count_messages(user_id)
    chats = await db.count_chats(user_id)
    _, cur = get_currency(user["country"])
    voice_map = VOICES.get(lang, VOICES["en"])
    voice_name = voice_map.get(user["ai_voice"], user["ai_voice"])

    reg_date = user["date_reg"].date() if user["date_reg"] else date.today()
    days = (date.today() - reg_date).days

    info = t(
        "account_info", lang,
        user_id=user_id,
        name=user["user_name"],
        date=reg_date.strftime("%d.%m.%Y"),
        days=f"{days}d",
        balance=round(float(user["balance"]), 2),
        cur=cur,
        model=user["ai_model"],
        voice=voice_name,
        msgs=msgs,
        chats=chats,
        country=user["country"] or "—",
        refs=refs,
        ref_link=f"{settings.telegram.bot_url}?start={user_id}",
    )

    await callback.message.edit_text(info, parse_mode="Markdown", reply_markup=account_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "change_model")
async def change_model_menu(callback: CallbackQuery, lang: str = "en"):
    await callback.message.edit_text(
        t("select_model", lang),
        reply_markup=model_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("model:"))
async def set_model(callback: CallbackQuery, lang: str = "en"):
    model = callback.data.split(":")[1]
    await db.update_user(callback.from_user.id, ai_model=model)
    await callback.message.edit_text(
        t("model_changed", lang),
        reply_markup=back_keyboard(lang, "account"),
    )
    await callback.answer()


@router.callback_query(F.data == "change_voice")
async def change_voice_menu(callback: CallbackQuery, lang: str = "en"):
    await callback.message.edit_text(
        t("select_voice", lang),
        reply_markup=voice_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_voice:"))
async def set_voice(callback: CallbackQuery, lang: str = "en"):
    voice = callback.data.split(":")[1]
    await db.update_user(callback.from_user.id, ai_voice=voice)
    await callback.message.edit_text(
        t("voice_changed", lang),
        reply_markup=back_keyboard(lang, "account"),
    )
    await callback.answer()


@router.callback_query(F.data == "change_lang")
async def change_lang_menu(callback: CallbackQuery):
    from app.keyboards import language_keyboard
    await callback.message.edit_text(
        t("choose_language", "en"),
        reply_markup=language_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "change_country")
async def change_country_menu(callback: CallbackQuery, lang: str = "en"):
    from app.keyboards import country_keyboard
    await callback.message.edit_text(
        t("choose_country", lang),
        reply_markup=country_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "prices")
async def show_prices(callback: CallbackQuery, lang: str = "en"):
    await callback.message.edit_text(
        t("prices", lang),
        parse_mode="Markdown",
        reply_markup=back_keyboard(lang, "account"),
    )
    await callback.answer()


@router.callback_query(F.data == "chats_menu")
async def chats_menu(callback: CallbackQuery, lang: str = "en"):
    await callback.message.edit_text(
        "💬",
        reply_markup=chats_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "get_all_chats")
async def get_all_chats(callback: CallbackQuery, lang: str = "en"):
    user_id = callback.from_user.id
    chat_ids = await db.get_all_chat_ids(user_id, closed_only=True)
    if not chat_ids:
        await callback.message.edit_text("📭 —", reply_markup=back_keyboard(lang, "chats_menu"))
        await callback.answer()
        return

    lines = [f"💬 Chat #{cid}" for cid in chat_ids[-30:]]
    text = f"*{t('btn_my_chats', lang)}*\n\n" + "\n".join(lines)
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_keyboard(lang, "chats_menu"))
    await callback.answer()


@router.callback_query(F.data == "get_one_chat")
async def get_one_chat(callback: CallbackQuery, lang: str = "en"):
    user_id = callback.from_user.id
    chat_ids = await db.get_all_chat_ids(user_id, closed_only=True)
    if not chat_ids:
        await callback.message.edit_text("📭 —", reply_markup=back_keyboard(lang, "chats_menu"))
        await callback.answer()
        return

    last_chat_id = chat_ids[-1]
    msgs = await db.get_chat_messages(user_id, last_chat_id)
    lines = []
    for m in msgs[-15:]:
        role = "🤖" if m["role"] == "assistant" else "👤"
        content = (m["content"] or "")[:200]
        lines.append(f"{role} {content}")

    text = f"*Chat #{last_chat_id}*\n\n" + "\n\n".join(lines)
    await callback.message.edit_text(text[:4096], parse_mode="Markdown", reply_markup=back_keyboard(lang, "chats_menu"))
    await callback.answer()


@router.callback_query(F.data == "delete_history")
async def delete_history(callback: CallbackQuery, lang: str = "en"):
    await db.delete_user_history(callback.from_user.id)
    await callback.message.edit_text(
        t("history_deleted", lang),
        reply_markup=back_keyboard(lang, "account"),
    )
    await callback.answer()


@router.callback_query(F.data == "close_msg")
async def close_msg(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer()
