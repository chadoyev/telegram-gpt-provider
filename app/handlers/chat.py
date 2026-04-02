from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from io import BytesIO

from aiogram import Router, F, Bot
from aiogram.enums import ChatAction
from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile

from app import db
from app.billing import (
    calculate_cost_usd, charge_user, check_balance,
    charge_whisper, charge_tts, charge_image, get_currency,
)
from app.chat_export import export_single_chat
from app.config import settings
from app.keyboards import chat_keyboard, welcome_keyboard, close_keyboard
from app.locales import t
from app.openai_client import (
    chat_stream, transcribe_audio, text_to_speech,
    is_supported_file, is_image_file, generate_image,
    IMAGE_GEN_TOOL,
)
from app.utils import (
    convert_ogg_to_mp3, convert_mp3_to_ogg, file_to_base64,
    ensure_user_dir, get_audio_duration,
)

log = logging.getLogger(__name__)
router = Router(name="chat")

DRAFT_UPDATE_INTERVAL = 0.8

_last_kb_msg: dict[int, int] = {}


async def _delete_after(bot: Bot, chat_id: int, message_id: int, delay: float = 4):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception:
        pass


async def _notify_no_chat(message: Message, bot: Bot, lang: str):
    """Delete user message and show a temporary auto-deleting notification."""
    try:
        await message.delete()
    except Exception:
        pass
    try:
        notif = await bot.send_message(message.from_user.id, t("no_active_chat", lang))
        asyncio.create_task(_delete_after(bot, message.from_user.id, notif.message_id))
    except Exception:
        pass


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

    msg = await callback.message.edit_text(
        t("chat_started", lang),
        reply_markup=chat_keyboard(lang, user["voice_enabled"]),
    )
    await db.track_message(user_id, chat_id, msg.message_id)
    _last_kb_msg[user_id] = msg.message_id
    await callback.answer()


@router.callback_query(F.data == "end_chat")
async def end_chat(callback: CallbackQuery, bot: Bot, lang: str = "en"):
    user_id = callback.from_user.id
    chat_id = await db.get_current_chat_id(user_id)
    _last_kb_msg.pop(user_id, None)

    if chat_id:
        tg_msgs = await db.get_tracked_messages(user_id, chat_id)
        for msg_id in tg_msgs:
            try:
                await bot.delete_message(user_id, msg_id)
            except Exception:
                pass
        await db.delete_tracked_messages(user_id, chat_id)

        await db.close_chat(user_id, chat_id)

        total_spent = await db.get_chat_total_spending(user_id, chat_id)
        if total_spent > 0:
            user = await db.get_user(user_id)
            country = user["country"] if user else "Другое"
            cur_code, _ = get_currency(country)
            await db.create_transaction(
                user_id, 6, total_spent, cur_code,
                chat_number=chat_id, description="Chat payment",
            )

        try:
            file_path = await export_single_chat(user_id, chat_id, lang)
            doc = FSInputFile(file_path)
            await bot.send_document(
                user_id, doc,
                caption=t("your_chat_file", lang),
                reply_markup=close_keyboard(lang),
            )
        except Exception as e:
            log.error("Chat export error: %s", e)

    await db.update_user(user_id, status_chat=False)
    await bot.send_message(
        user_id,
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


async def _remove_prev_keyboard(bot: Bot, user_id: int):
    """Remove inline keyboard from the previous bot message."""
    prev_msg = _last_kb_msg.pop(user_id, None)
    if prev_msg:
        try:
            await bot.edit_message_reply_markup(
                chat_id=user_id, message_id=prev_msg, reply_markup=None,
            )
        except Exception:
            pass


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
) -> tuple[str, str, int, str | None]:
    """Stream via sendMessageDraft, finalize with sendMessage.
    Returns (full_text, spending, tg_message_id, gen_image_path)."""
    user = await db.get_user(user_id)
    model = user["ai_model"]
    country = user["country"]
    voice_on = user["voice_enabled"]

    bs = await db.get_bot_settings()
    temperature = float(bs["temperature"])
    max_tokens = bs["max_tokens"]

    accumulated = ""
    last_update = 0.0
    input_tokens = 0
    output_tokens = 0
    function_calls = []
    draft_id = int(time.time() * 1000) % (2**31 - 1) or 1

    await bot.send_chat_action(user_id, ChatAction.TYPING)

    try:
        async for chunk in chat_stream(
            history=history,
            text=text,
            image_b64=image_b64,
            file_b64=file_b64,
            file_name=file_name,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            tools=[IMAGE_GEN_TOOL],
        ):
            if isinstance(chunk, dict):
                if chunk["type"] == "usage":
                    input_tokens = chunk["input_tokens"]
                    output_tokens = chunk["output_tokens"]
                elif chunk["type"] == "function_call":
                    function_calls.append(chunk)
                continue

            accumulated += chunk
            now = time.monotonic()

            if accumulated and now - last_update >= DRAFT_UPDATE_INTERVAL:
                try:
                    await bot.send_message_draft(
                        chat_id=user_id,
                        draft_id=draft_id,
                        text=accumulated[:4096],
                    )
                except Exception as e:
                    log.debug("Draft update failed: %s", e)
                last_update = now

    except Exception as e:
        log.error("Stream error: %s", e)
        if not accumulated:
            accumulated = t("error_ai_overloaded", lang)

    # Send final draft with complete text before materializing
    if accumulated:
        try:
            await bot.send_message_draft(
                chat_id=user_id,
                draft_id=draft_id,
                text=accumulated[:4096],
            )
        except Exception:
            pass

    # Handle function calls (image generation in chat)
    generated_photo = None
    gen_image_path = None
    for fc in function_calls:
        if fc["name"] == "generate_image":
            try:
                args = json.loads(fc["arguments"])
                prompt = args.get("prompt", "")
                if prompt:
                    image_bytes = await generate_image(prompt)
                    generated_photo = BufferedInputFile(image_bytes, filename="generated.png")
                    await charge_image(user_id, country)
                    img_dir = ensure_user_dir(user_id)
                    gen_image_path = str(img_dir / f"gen_{chat_id}_{int(time.time())}.png")
                    with open(gen_image_path, "wb") as f:
                        f.write(image_bytes)
                    if not accumulated:
                        accumulated = t("img_gen_done", lang)
            except Exception as e:
                log.error("In-chat image gen error: %s", e)
                if not accumulated:
                    accumulated = t("error_ai_overloaded", lang)

    # Calculate costs
    if input_tokens == 0:
        input_tokens = len((text or "").split()) * 2
    if output_tokens == 0:
        output_tokens = len(accumulated.split()) * 2

    cost_usd = 0.0
    try:
        cost_usd = await calculate_cost_usd(input_tokens, output_tokens, model)
        cost_local, new_balance = await charge_user(user_id, cost_usd, country)
    except Exception:
        cost_local, new_balance = 0.0, await db.get_balance(user_id)

    spending = f"{input_tokens}~{output_tokens}~{round(cost_local, 4)}~{round(new_balance, 4)}~{model}"

    _, cur_symbol = get_currency(country)
    parts = spending.split("~")
    tokens_info = t(
        "spending_line", lang,
        tokens=f"{parts[0]}/{parts[1]}",
        cost=parts[2], cur=cur_symbol,
        balance=parts[3],
    )

    kb = chat_keyboard(lang, voice_on)

    if generated_photo:
        # Consume the streaming draft with a temp message and remove it
        try:
            temp_msg = await bot.send_message(chat_id=user_id, text="⏳")
            await bot.delete_message(user_id, temp_msg.message_id)
        except Exception:
            pass

        max_caption = 1024 - len(tokens_info) - 10
        caption = accumulated[:max_caption] + tokens_info if accumulated else tokens_info
        try:
            msg = await bot.send_photo(
                chat_id=user_id, photo=generated_photo,
                caption=caption, reply_markup=kb,
            )
        except Exception:
            msg = await bot.send_photo(
                chat_id=user_id, photo=generated_photo,
                caption=tokens_info, reply_markup=kb,
            )
    else:
        max_len = 4096 - len(tokens_info) - 10
        final_text = accumulated[:max_len] + tokens_info if accumulated else tokens_info
        try:
            msg = await bot.send_message(
                chat_id=user_id, text=final_text,
                parse_mode="Markdown", reply_markup=kb,
            )
        except Exception:
            msg = await bot.send_message(
                chat_id=user_id, text=final_text,
                reply_markup=kb,
            )

    await db.track_message(user_id, chat_id, msg.message_id)
    _last_kb_msg[user_id] = msg.message_id

    return accumulated, spending, msg.message_id, gen_image_path, cost_usd


async def _send_voice_reply(
    bot: Bot, user_id: int, chat_id: int,
    text: str, user, lang: str,
) -> str | None:
    """Send TTS voice reply and track it. Returns ogg file path."""
    try:
        user_dir = ensure_user_dir(user["user_id"])
        mp3_path = str(user_dir / f"tts_{int(time.time())}.mp3")
        await text_to_speech(text[:4096], voice=user["ai_voice"], output_path=mp3_path)
        ogg_path = await convert_mp3_to_ogg(mp3_path)

        await charge_tts(user["user_id"], len(text), user["country"])

        voice_file = FSInputFile(ogg_path)
        voice_msg = await bot.send_voice(chat_id=user_id, voice=voice_file)
        await db.track_message(user_id, chat_id, voice_msg.message_id)

        try:
            os.unlink(mp3_path)
        except OSError:
            pass
        return ogg_path
    except Exception as e:
        log.error("TTS error: %s", e)
        return None


@router.message(F.text)
async def handle_text(message: Message, bot: Bot, db_user=None, lang: str = "en"):
    if not db_user:
        return
    user_id = message.from_user.id

    from app.handlers.admin import try_admin_command
    if await try_admin_command(message):
        return

    if not db_user["status_chat"]:
        await _notify_no_chat(message, bot, lang)
        return

    if not await check_balance(user_id, 0.001, db_user["country"]):
        await message.answer(t("insufficient_funds", lang))
        return

    chat_id = await db.get_current_chat_id(user_id)
    history = await _get_history(user_id, chat_id)

    await db.track_message(user_id, chat_id, message.message_id)
    await db.save_message(user_id, chat_id, "user", message.text, model=db_user["ai_model"])

    await _remove_prev_keyboard(bot, user_id)

    full_text, spending, msg_id, gen_img_path, cost_usd = await _stream_response(
        bot, user_id, chat_id, history,
        text=message.text, lang=lang,
    )

    tts_path = None
    user = await db.get_user(user_id)
    if user and user["voice_enabled"]:
        tts_path = await _send_voice_reply(bot, user_id, chat_id, full_text, user, lang)

    asst_ft, asst_fp = ("photo", gen_img_path) if gen_img_path else ("voice", tts_path) if tts_path else (None, None)
    await db.save_message(
        user_id, chat_id, "assistant", full_text,
        model=db_user["ai_model"], spending=spending,
        file_type=asst_ft, file_path=asst_fp, cost_usd=cost_usd,
    )


@router.message(F.voice)
async def handle_voice(message: Message, bot: Bot, db_user=None, lang: str = "en"):
    if not db_user or not db_user["status_chat"]:
        await _notify_no_chat(message, bot, lang)
        return

    user_id = message.from_user.id
    chat_id = await db.get_current_chat_id(user_id)

    await db.track_message(user_id, chat_id, message.message_id)

    await bot.send_chat_action(user_id, ChatAction.TYPING)

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
        await message.answer(t("voice_empty", lang))
        return

    if not text.strip():
        await message.answer(t("voice_empty", lang))
        return

    await charge_whisper(user_id, duration, db_user["country"])

    history = await _get_history(user_id, chat_id)
    await db.save_message(
        user_id, chat_id, "user", text,
        model="whisper", file_type="voice", file_path=ogg_path,
    )

    await _remove_prev_keyboard(bot, user_id)

    full_text, spending, msg_id, gen_img_path, cost_usd = await _stream_response(
        bot, user_id, chat_id, history, text=text, lang=lang,
    )

    tts_path = None
    user = await db.get_user(user_id)
    if user and user["voice_enabled"]:
        tts_path = await _send_voice_reply(bot, user_id, chat_id, full_text, user, lang)

    asst_ft, asst_fp = ("photo", gen_img_path) if gen_img_path else ("voice", tts_path) if tts_path else (None, None)
    await db.save_message(
        user_id, chat_id, "assistant", full_text,
        model=db_user["ai_model"], spending=spending,
        file_type=asst_ft, file_path=asst_fp, cost_usd=cost_usd,
    )

    try:
        os.unlink(mp3_path)
    except OSError:
        pass


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot, db_user=None, lang: str = "en"):
    if not db_user or not db_user["status_chat"]:
        await _notify_no_chat(message, bot, lang)
        return

    user_id = message.from_user.id
    chat_id = await db.get_current_chat_id(user_id)

    await db.track_message(user_id, chat_id, message.message_id)

    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    photo_bytes = BytesIO()
    await bot.download_file(file_info.file_path, photo_bytes)
    image_b64 = __import__("base64").b64encode(photo_bytes.getvalue()).decode()

    user_dir = ensure_user_dir(user_id)
    photo_path = str(user_dir / f"photo_{chat_id}_{int(time.time())}.jpg")
    with open(photo_path, "wb") as f:
        f.write(photo_bytes.getvalue())

    caption = message.caption or "Что на этом изображении?"

    history = await _get_history(user_id, chat_id)
    await db.save_message(
        user_id, chat_id, "user", caption,
        model=db_user["ai_model"], file_type="photo", file_path=photo_path,
    )

    await _remove_prev_keyboard(bot, user_id)

    full_text, spending, msg_id, gen_img_path, cost_usd = await _stream_response(
        bot, user_id, chat_id, history,
        text=caption, image_b64=image_b64, lang=lang,
    )

    tts_path = None
    user = await db.get_user(user_id)
    if user and user["voice_enabled"]:
        tts_path = await _send_voice_reply(bot, user_id, chat_id, full_text, user, lang)

    asst_ft, asst_fp = ("photo", gen_img_path) if gen_img_path else ("voice", tts_path) if tts_path else (None, None)
    await db.save_message(
        user_id, chat_id, "assistant", full_text,
        model=db_user["ai_model"], spending=spending,
        file_type=asst_ft, file_path=asst_fp, cost_usd=cost_usd,
    )


@router.message(F.document)
async def handle_document(message: Message, bot: Bot, db_user=None, lang: str = "en"):
    if not db_user or not db_user["status_chat"]:
        await _notify_no_chat(message, bot, lang)
        return

    user_id = message.from_user.id
    doc = message.document
    file_name = doc.file_name or "file"

    if not is_supported_file(file_name):
        await message.answer(t("file_unsupported", lang))
        return

    chat_id = await db.get_current_chat_id(user_id)

    await db.track_message(user_id, chat_id, message.message_id)

    file_info = await bot.get_file(doc.file_id)
    file_bytes = BytesIO()
    await bot.download_file(file_info.file_path, file_bytes)

    user_dir = ensure_user_dir(user_id)
    from pathlib import Path as _Path
    safe_name = _Path(file_name).name
    doc_path = str(user_dir / f"doc_{int(time.time())}_{safe_name}")
    with open(doc_path, "wb") as f:
        f.write(file_bytes.getvalue())

    if is_image_file(file_name):
        image_b64 = __import__("base64").b64encode(file_bytes.getvalue()).decode()
        file_b64 = None
    else:
        image_b64 = None
        file_b64 = __import__("base64").b64encode(file_bytes.getvalue()).decode()

    caption = message.caption or f"Проанализируй файл {file_name}"

    history = await _get_history(user_id, chat_id)
    await db.save_message(
        user_id, chat_id, "user", caption,
        model=db_user["ai_model"], file_type="document", file_path=doc_path,
    )

    await _remove_prev_keyboard(bot, user_id)

    full_text, spending, msg_id, gen_img_path, cost_usd = await _stream_response(
        bot, user_id, chat_id, history,
        text=caption, image_b64=image_b64,
        file_b64=file_b64, file_name=file_name, lang=lang,
    )

    tts_path = None
    user = await db.get_user(user_id)
    if user and user["voice_enabled"]:
        tts_path = await _send_voice_reply(bot, user_id, chat_id, full_text, user, lang)

    asst_ft, asst_fp = ("photo", gen_img_path) if gen_img_path else ("voice", tts_path) if tts_path else (None, None)
    await db.save_message(
        user_id, chat_id, "assistant", full_text,
        model=db_user["ai_model"], spending=spending,
        file_type=asst_ft, file_path=asst_fp, cost_usd=cost_usd,
    )


@router.message()
async def handle_any(message: Message, bot: Bot, db_user=None, lang: str = "en"):
    """Catch-all: notify if chat not started, ignore otherwise."""
    if not db_user or not db_user["status_chat"]:
        await _notify_no_chat(message, bot, lang)
        return
