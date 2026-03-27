from __future__ import annotations

import asyncio
import logging
import os
import time
from io import BytesIO

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile

from app import db
from app.billing import (
    calculate_cost_usd, charge_user, check_balance,
    charge_whisper, charge_tts, get_currency,
)
from app.config import settings
from app.keyboards import chat_keyboard, welcome_keyboard, close_keyboard
from app.locales import t
from app.openai_client import (
    chat_stream, transcribe_audio, text_to_speech,
    is_supported_file, is_image_file,
)
from app.utils import (
    convert_ogg_to_mp3, convert_mp3_to_ogg, file_to_base64,
    ensure_user_dir, get_audio_duration,
)

log = logging.getLogger(__name__)
router = Router(name="chat")

STREAM_UPDATE_INTERVAL = 1.0
MIN_CHUNK_SIZE = 80


@router.callback_query(F.data == "start_chat")
async def start_chat(callback: CallbackQuery, lang: str = "en"):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.answer()
        return

    if user["status_chat"]:
        await callback.answer(t("already_has_chat", lang), show_alert=True)
        return

    chat_id = await db.get_next_chat_id(user_id)
    await db.update_user(user_id, status_chat=True)
    await db.save_message(user_id, chat_id, "system", "Chat started", model="system")

    await callback.message.edit_text(
        t("chat_started", lang),
        reply_markup=chat_keyboard(lang, user["voice_enabled"]),
    )
    await callback.answer()


@router.callback_query(F.data == "end_chat")
async def end_chat(callback: CallbackQuery, lang: str = "en"):
    user_id = callback.from_user.id
    chat_id = await db.get_current_chat_id(user_id)
    if chat_id:
        await db.close_chat(user_id, chat_id)
    await db.update_user(user_id, status_chat=False)

    await callback.message.edit_text(
        t("chat_ended", lang),
        reply_markup=welcome_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "voice_on")
async def voice_on(callback: CallbackQuery, lang: str = "en"):
    await db.update_user(callback.from_user.id, voice_enabled=True)
    await callback.message.edit_reply_markup(reply_markup=chat_keyboard(lang, True))
    await callback.answer()


@router.callback_query(F.data == "voice_off")
async def voice_off(callback: CallbackQuery, lang: str = "en"):
    await db.update_user(callback.from_user.id, voice_enabled=False)
    await callback.message.edit_reply_markup(reply_markup=chat_keyboard(lang, False))
    await callback.answer()


async def _get_history(user_id: int, chat_id: int) -> list[dict]:
    rows = await db.get_chat_messages(user_id, chat_id)
    history = []
    for r in rows:
        if r["role"] in ("user", "assistant"):
            history.append({"role": r["role"], "content": r["content"] or ""})
    return history[-20:]


async def _stream_response(
    bot: Bot,
    user_id: int,
    chat_id: int,
    history: list[dict],
    text: str | None = None,
    image_b64: str | None = None,
    file_b64: str | None = None,
    file_name: str | None = None,
    lang: str = "en",
) -> tuple[str, str]:
    """Stream AI response to user via message drafts, return (full_text, spending_info)."""
    user = await db.get_user(user_id)
    model = user["ai_model"]
    country = user["country"]
    _, cur_symbol = get_currency(country)

    bs = await db.get_bot_settings()
    temperature = float(bs["temperature"])
    max_tokens = bs["max_tokens"]

    accumulated = ""
    last_update = 0.0
    draft_id = int(time.time() * 1000) % (2**31 - 1)
    if draft_id == 0:
        draft_id = 1

    try:
        draft_sent = False
        async for chunk in chat_stream(
            history=history,
            text=text,
            image_b64=image_b64,
            file_b64=file_b64,
            file_name=file_name,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        ):
            accumulated += chunk
            now = time.monotonic()
            if (now - last_update >= STREAM_UPDATE_INTERVAL
                    and len(accumulated) >= MIN_CHUNK_SIZE):
                try:
                    display = accumulated[:4000]
                    await bot.send_message_draft(
                        chat_id=user_id,
                        draft_id=draft_id,
                        text=display,
                    )
                    draft_sent = True
                    last_update = now
                except Exception as e:
                    log.debug("Draft update failed: %s", e)

    except Exception as e:
        log.error("Stream error: %s", e)
        if not accumulated:
            accumulated = t("error_ai_overloaded", lang)

    input_tokens = len((text or "").split()) * 2
    output_tokens = len(accumulated.split()) * 2

    try:
        cost_usd = await calculate_cost_usd(input_tokens, output_tokens, model)
        cost_local, new_balance = await charge_user(user_id, cost_usd, country)
    except Exception:
        cost_local, new_balance = 0.0, await db.get_balance(user_id)

    spending = f"{input_tokens}~{output_tokens}~{round(cost_local, 4)}~{round(new_balance, 4)}~{model}"
    return accumulated, spending


@router.message(F.text)
async def handle_text(message: Message, bot: Bot, db_user=None, lang: str = "en"):
    if not db_user:
        return
    user_id = message.from_user.id

    if not db_user["status_chat"]:
        await message.answer(t("no_active_chat", lang), reply_markup=welcome_keyboard(lang))
        return

    if not await check_balance(user_id, 0.001, db_user["country"]):
        await message.answer(t("insufficient_funds", lang))
        return

    chat_id = await db.get_current_chat_id(user_id)
    history = await _get_history(user_id, chat_id)

    status_msg = await message.answer(t("thinking", lang))

    await db.save_message(user_id, chat_id, "user", message.text, model=db_user["ai_model"])

    full_text, spending = await _stream_response(
        bot, user_id, chat_id, history,
        text=message.text, lang=lang,
    )

    _, cur_symbol = get_currency(db_user["country"])
    parts = spending.split("~")
    tokens_info = t(
        "spending_line", lang,
        tokens=f"{parts[0]}/{parts[1]}",
        cost=parts[2], cur=cur_symbol,
        balance=parts[3],
    )

    final_text = full_text[:4000] + tokens_info
    try:
        await status_msg.edit_text(final_text, parse_mode="Markdown")
    except Exception:
        try:
            await status_msg.edit_text(final_text)
        except Exception:
            await message.answer(final_text[:4096])

    await db.save_message(
        user_id, chat_id, "assistant", full_text,
        model=db_user["ai_model"], spending=spending,
    )

    user = await db.get_user(user_id)
    if user and user["voice_enabled"]:
        await _send_voice_reply(message, bot, full_text, user, lang)


@router.message(F.voice)
async def handle_voice(message: Message, bot: Bot, db_user=None, lang: str = "en"):
    if not db_user or not db_user["status_chat"]:
        await message.answer(t("no_active_chat", lang))
        return

    user_id = message.from_user.id
    status_msg = await message.answer(t("recognize_voice", lang))

    user_dir = ensure_user_dir(user_id)
    ogg_path = str(user_dir / f"voice_{int(time.time())}.ogg")

    file_info = await bot.get_file(message.voice.file_id)
    await bot.download_file(file_info.file_path, ogg_path)

    mp3_path = await convert_ogg_to_mp3(ogg_path)
    duration = await get_audio_duration(mp3_path)

    try:
        text = await transcribe_audio(mp3_path)
    except Exception as e:
        log.error("Whisper error: %s", e)
        await status_msg.edit_text(t("voice_empty", lang))
        return

    if not text.strip():
        await status_msg.edit_text(t("voice_empty", lang))
        return

    await charge_whisper(user_id, duration, db_user["country"])

    chat_id = await db.get_current_chat_id(user_id)
    history = await _get_history(user_id, chat_id)
    await db.save_message(user_id, chat_id, "user", text, model="whisper", file_type="voice", file_path=ogg_path)

    full_text, spending = await _stream_response(
        bot, user_id, chat_id, history, text=text, lang=lang,
    )

    _, cur_symbol = get_currency(db_user["country"])
    parts = spending.split("~")
    tokens_info = t(
        "spending_line", lang,
        tokens=f"{parts[0]}/{parts[1]}",
        cost=parts[2], cur=cur_symbol,
        balance=parts[3],
    )

    await status_msg.edit_text(full_text[:4000] + tokens_info, parse_mode="Markdown")
    await db.save_message(user_id, chat_id, "assistant", full_text, model=db_user["ai_model"], spending=spending)

    user = await db.get_user(user_id)
    if user and user["voice_enabled"]:
        await _send_voice_reply(message, bot, full_text, user, lang)

    for p in (ogg_path, mp3_path):
        try:
            os.unlink(p)
        except OSError:
            pass


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot, db_user=None, lang: str = "en"):
    if not db_user or not db_user["status_chat"]:
        await message.answer(t("no_active_chat", lang))
        return

    user_id = message.from_user.id
    status_msg = await message.answer(t("thinking", lang))

    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    photo_bytes = BytesIO()
    await bot.download_file(file_info.file_path, photo_bytes)
    image_b64 = __import__("base64").b64encode(photo_bytes.getvalue()).decode()

    caption = message.caption or "Что на этом изображении?"

    chat_id = await db.get_current_chat_id(user_id)
    history = await _get_history(user_id, chat_id)
    await db.save_message(user_id, chat_id, "user", caption, model=db_user["ai_model"], file_type="photo")

    full_text, spending = await _stream_response(
        bot, user_id, chat_id, history,
        text=caption, image_b64=image_b64, lang=lang,
    )

    _, cur_symbol = get_currency(db_user["country"])
    parts = spending.split("~")
    tokens_info = t(
        "spending_line", lang,
        tokens=f"{parts[0]}/{parts[1]}",
        cost=parts[2], cur=cur_symbol,
        balance=parts[3],
    )

    await status_msg.edit_text(full_text[:4000] + tokens_info, parse_mode="Markdown")
    await db.save_message(user_id, chat_id, "assistant", full_text, model=db_user["ai_model"], spending=spending)


@router.message(F.document)
async def handle_document(message: Message, bot: Bot, db_user=None, lang: str = "en"):
    if not db_user or not db_user["status_chat"]:
        await message.answer(t("no_active_chat", lang))
        return

    user_id = message.from_user.id
    doc = message.document
    file_name = doc.file_name or "file"

    if not is_supported_file(file_name):
        await message.answer(t("file_unsupported", lang))
        return

    status_msg = await message.answer(t("file_received", lang))

    file_info = await bot.get_file(doc.file_id)
    file_bytes = BytesIO()
    await bot.download_file(file_info.file_path, file_bytes)

    if is_image_file(file_name):
        image_b64 = __import__("base64").b64encode(file_bytes.getvalue()).decode()
        file_b64 = None
    else:
        image_b64 = None
        file_b64 = __import__("base64").b64encode(file_bytes.getvalue()).decode()

    caption = message.caption or f"Проанализируй файл {file_name}"

    chat_id = await db.get_current_chat_id(user_id)
    history = await _get_history(user_id, chat_id)
    await db.save_message(
        user_id, chat_id, "user", caption,
        model=db_user["ai_model"], file_type="document", file_path=file_name,
    )

    full_text, spending = await _stream_response(
        bot, user_id, chat_id, history,
        text=caption, image_b64=image_b64,
        file_b64=file_b64, file_name=file_name, lang=lang,
    )

    _, cur_symbol = get_currency(db_user["country"])
    parts = spending.split("~")
    tokens_info = t(
        "spending_line", lang,
        tokens=f"{parts[0]}/{parts[1]}",
        cost=parts[2], cur=cur_symbol,
        balance=parts[3],
    )

    await status_msg.edit_text(full_text[:4000] + tokens_info, parse_mode="Markdown")
    await db.save_message(user_id, chat_id, "assistant", full_text, model=db_user["ai_model"], spending=spending)


async def _send_voice_reply(message: Message, bot: Bot, text: str, user, lang: str):
    try:
        user_dir = ensure_user_dir(user["user_id"])
        mp3_path = str(user_dir / f"tts_{int(time.time())}.mp3")
        await text_to_speech(text[:4096], voice=user["ai_voice"], output_path=mp3_path)
        ogg_path = await convert_mp3_to_ogg(mp3_path)

        await charge_tts(user["user_id"], len(text), user["country"])

        voice_file = FSInputFile(ogg_path)
        await message.answer_voice(voice_file)

        for p in (mp3_path, ogg_path):
            try:
                os.unlink(p)
            except OSError:
                pass
    except Exception as e:
        log.error("TTS error: %s", e)
