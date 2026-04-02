from __future__ import annotations

import logging
from datetime import date

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, FSInputFile

from app import db
from app.billing import get_currency, get_exchange_rate, format_prices_markdown
from app.chat_export import export_single_chat, export_all_chats
from app.config import settings, VOICES
from app.keyboards import (
    account_keyboard, model_keyboard, voice_keyboard,
    chats_menu_keyboard, back_keyboard, welcome_keyboard,
    close_keyboard, chat_number_keyboard,
)
from app.locales import t

log = logging.getLogger(__name__)
router = Router(name="menu")


async def send_account_page(bot: Bot, user_id: int, lang: str) -> None:
    """Send the full account info page as a new message."""
    user = await db.get_user(user_id)
    if not user:
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
    await bot.send_message(user_id, info, parse_mode="Markdown", reply_markup=account_keyboard(lang))


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
    text = await format_prices_markdown(lang)
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=back_keyboard(lang, "account"),
    )
    await callback.answer()


@router.callback_query(F.data == "chats_menu")
async def chats_menu(callback: CallbackQuery, lang: str = "en"):
    await callback.message.edit_text(
        t("chats_menu_text", lang),
        reply_markup=chats_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "get_all_chats")
async def get_all_chats(callback: CallbackQuery, bot: Bot, lang: str = "en"):
    user_id = callback.from_user.id
    chat_ids = await db.get_all_chat_ids(user_id, closed_only=True)
    if not chat_ids:
        await callback.message.edit_text("📭 —", reply_markup=back_keyboard(lang, "chats_menu"))
        await callback.answer()
        return

    await callback.message.edit_text(t("collecting_chats", lang))

    try:
        file_path = await export_all_chats(user_id, lang)
        doc = FSInputFile(file_path)
        await callback.message.answer_document(
            doc,
            caption=t("your_chats_file", lang),
            reply_markup=close_keyboard(lang),
        )
        try:
            await callback.message.delete()
        except Exception:
            pass
        await send_account_page(bot, user_id, lang)
    except Exception as e:
        log.error("All chats export error: %s", e)
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

    await callback.message.edit_text(
        t("enter_chat_number", lang),
        reply_markup=chat_number_keyboard(lang, chat_ids[-10:]),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("export_chat:"))
async def export_specific_chat(callback: CallbackQuery, lang: str = "en"):
    user_id = callback.from_user.id
    try:
        chat_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer(t("unexpected_error", lang), show_alert=True)
        return

    try:
        await callback.message.delete()
    except Exception:
        pass

    try:
        file_path = await export_single_chat(user_id, chat_id, lang)
        doc = FSInputFile(file_path)
        await callback.message.answer_document(
            doc,
            caption=t("your_chat_file", lang),
            reply_markup=close_keyboard(lang),
        )
    except Exception as e:
        log.error("Chat export error: %s", e)
        await callback.message.answer(
            t("unexpected_error", lang),
            reply_markup=back_keyboard(lang, "chats_menu"),
        )

    chat_ids = await db.get_all_chat_ids(user_id, closed_only=True)
    if chat_ids:
        await callback.message.answer(
            t("enter_chat_number", lang),
            reply_markup=chat_number_keyboard(lang, chat_ids[-10:]),
        )

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
