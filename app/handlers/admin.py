from __future__ import annotations

import asyncio
import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

from app import db
from app.config import settings

log = logging.getLogger(__name__)
router = Router(name="admin")


class AdminStates(StatesGroup):
    waiting_setting_value = State()
    waiting_add_balance = State()
    waiting_broadcast_msg = State()


def _is_admin(user_id: int) -> bool:
    return user_id == settings.telegram.admin_id


def _fmt(val) -> str:
    return f"{float(val):g}"


# ── Keyboards ────────────────────────────────────────────────────

def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="adm_refresh")],
        [InlineKeyboardButton(text="⚡ Вкл/Выкл бот", callback_data="adm_toggle")],
        [
            InlineKeyboardButton(text="📝 Токены", callback_data="adm_set:max_tokens"),
            InlineKeyboardButton(text="🌡 Температура", callback_data="adm_set:temperature"),
        ],
        [
            InlineKeyboardButton(text="🎁 Бонус пригл.", callback_data="adm_set:referral_bonus"),
            InlineKeyboardButton(text="🎁 Бонус рефер.", callback_data="adm_set:reffer_bonus"),
        ],
        [
            InlineKeyboardButton(text="📊 Наценка %", callback_data="adm_set:markup_percent"),
            InlineKeyboardButton(text="💎 Возн. %", callback_data="adm_set:referral_reward_percent"),
        ],
        [InlineKeyboardButton(text="💰 Пополнить баланс", callback_data="adm_add_balance")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="adm_broadcast")],
    ])


def _back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩ Назад", callback_data="adm_back")],
    ])


def _broadcast_preview_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📨 Отправить", callback_data="adm_bc_send"),
            InlineKeyboardButton(text="✏ Изменить", callback_data="adm_bc_edit"),
        ],
        [InlineKeyboardButton(text="↩ Назад", callback_data="adm_back")],
    ])


# ── Setting prompts ──────────────────────────────────────────────

_SETTING_PROMPTS = {
    "max_tokens": "📝 Введите новое количество токенов на чат (1 — 128000):",
    "temperature": "🌡 Введите новую температуру модели (0.0 — 2.0):",
    "referral_bonus": (
        "🎁 Введите бонус приглашающим в формате:\n"
        "`тенге-рубль-гривна-доллар`\n"
        "Пример: `10-45-5-0.1`"
    ),
    "reffer_bonus": (
        "🎁 Введите бонус рефералам в формате:\n"
        "`тенге-рубль-гривна-доллар`\n"
        "Пример: `5-20-2-0.05`"
    ),
    "markup_percent": "📊 Введите наценку на использование моделей (в %):",
    "referral_reward_percent": "💎 Введите % вознаграждения приглашающим от пополнений рефералов:",
}


# ── Admin panel text ─────────────────────────────────────────────

async def _admin_panel_text() -> str:
    bs = await db.get_bot_settings()
    users_count = await db.count_users()
    api_spending = await db.get_api_spending_30d()
    total_requests = await db.count_total_model_requests()

    markup = float(bs.get("markup_percent") or 0)
    markup_earnings = round(api_spending * markup / 100, 4) if markup > 0 else 0.0

    status_icon = "✅ Включён" if bs["status"] else "❌ Выключен"

    ref_bonus = (
        f"₸{_fmt(bs.get('referral_bonus_kzt') or 0)} / "
        f"₽{_fmt(bs.get('referral_bonus_rub') or 0)} / "
        f"₴{_fmt(bs.get('referral_bonus_uah') or 0)} / "
        f"${_fmt(bs.get('referral_bonus_usd') or 0)}"
    )
    reff_bonus = (
        f"₸{_fmt(bs.get('reffer_bonus_kzt') or 0)} / "
        f"₽{_fmt(bs.get('reffer_bonus_rub') or 0)} / "
        f"₴{_fmt(bs.get('reffer_bonus_uah') or 0)} / "
        f"${_fmt(bs.get('reffer_bonus_usd') or 0)}"
    )

    blocked = int(bs.get("blocked_users") or 0)
    reward_pct = _fmt(bs.get("referral_reward_percent") or 0)

    return (
        "⚙ *Админ-панель*\n\n"
        f"├👥 Пользователей: {users_count}\n"
        f"├⚡ Состояние: {status_icon}\n"
        f"├📝 Токены на чат: {bs['max_tokens']}\n"
        f"├🌡 Температура: {bs['temperature']}\n"
        f"├🎁 Бонус пригл.: {ref_bonus}\n"
        f"├🎁 Бонус рефер.: {reff_bonus}\n"
        f"├📊 Наценка: {_fmt(markup)}%\n"
        f"├💎 Возн. с попол.: {reward_pct}%\n"
        f"├💰 API за 30д: ${round(api_spending, 4)}\n"
        f"├📈 Наценка за 30д: ${round(markup_earnings, 4)}\n"
        f"├✉ Обращений к ИИ: {total_requests}\n"
        f"└🚫 Заблокировано: {blocked}"
    )


def _current_value_text(bs, key: str) -> str:
    if key in ("referral_bonus", "reffer_bonus"):
        return (
            f"₸{_fmt(bs.get(f'{key}_kzt') or 0)}-"
            f"₽{_fmt(bs.get(f'{key}_rub') or 0)}-"
            f"₴{_fmt(bs.get(f'{key}_uah') or 0)}-"
            f"${_fmt(bs.get(f'{key}_usd') or 0)}"
        )
    return str(bs.get(key, "?"))


# ── Entry point ──────────────────────────────────────────────────

async def try_admin_command(message: Message) -> bool:
    if not _is_admin(message.from_user.id):
        return False
    if message.text != settings.telegram.admin_password:
        return False

    try:
        await message.delete()
    except Exception:
        pass

    info = await _admin_panel_text()
    await message.answer(info, parse_mode="Markdown", reply_markup=admin_keyboard())
    return True


# ── Refresh ──────────────────────────────────────────────────────

@router.callback_query(F.data == "adm_refresh")
async def admin_refresh(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("♻Обновляю...")
    info = await _admin_panel_text()
    await callback.message.edit_text(info, parse_mode="Markdown", reply_markup=admin_keyboard())
    await callback.answer()


# ── Toggle bot status ────────────────────────────────────────────

@router.callback_query(F.data == "adm_toggle")
async def toggle_status(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        return
    bs = await db.get_bot_settings()
    new_status = not bs["status"]
    await db.update_bot_settings(status=new_status)
    info = await _admin_panel_text()
    await callback.message.edit_text(info, parse_mode="Markdown", reply_markup=admin_keyboard())
    await callback.answer(f"Бот {'включён' if new_status else 'выключен'}")


# ── Universal back ───────────────────────────────────────────────

@router.callback_query(F.data == "adm_back")
async def admin_back(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not _is_admin(callback.from_user.id):
        return

    data = await state.get_data()
    chat_id = callback.message.chat.id
    panel_msg_id = data.get("panel_msg_id")

    for key in ("preview_msg_id",):
        mid = data.get(key)
        if mid:
            try:
                await bot.delete_message(chat_id, mid)
            except Exception:
                pass

    for mid in data.get("admin_msg_ids", []):
        try:
            await bot.delete_message(chat_id, mid)
        except Exception:
            pass

    await state.clear()
    info = await _admin_panel_text()

    if panel_msg_id:
        try:
            await bot.edit_message_text(
                chat_id=chat_id, message_id=panel_msg_id,
                text=info, parse_mode="Markdown", reply_markup=admin_keyboard(),
            )
            if callback.message.message_id != panel_msg_id:
                try:
                    await callback.message.delete()
                except Exception:
                    pass
            await callback.answer()
            return
        except Exception:
            pass

    try:
        await callback.message.edit_text(info, parse_mode="Markdown", reply_markup=admin_keyboard())
    except Exception:
        await bot.send_message(chat_id, info, parse_mode="Markdown", reply_markup=admin_keyboard())
    await callback.answer()


# ── Editable settings (items 3–8) ───────────────────────────────

@router.callback_query(F.data.startswith("adm_set:"))
async def admin_setting_prompt(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        return
    key = callback.data.split(":")[1]
    prompt_text = _SETTING_PROMPTS.get(key, "Введите новое значение:")

    bs = await db.get_bot_settings()
    current = _current_value_text(bs, key)

    text = f"{prompt_text}\n\nТекущее значение: `{current}`"
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=_back_kb())
    await state.update_data(setting_key=key, panel_msg_id=callback.message.message_id)
    await state.set_state(AdminStates.waiting_setting_value)
    await callback.answer()


@router.message(AdminStates.waiting_setting_value, F.text)
async def admin_set_value(message: Message, state: FSMContext, bot: Bot):
    if not _is_admin(message.from_user.id):
        await state.clear()
        return

    data = await state.get_data()
    key = data.get("setting_key")
    panel_msg_id = data.get("panel_msg_id")

    try:
        if key == "max_tokens":
            val = int(message.text)
            assert 1 <= val <= 128000
            await db.update_bot_settings(max_tokens=val)
        elif key == "temperature":
            val = float(message.text.replace(",", "."))
            assert 0.0 <= val <= 2.0
            await db.update_bot_settings(temperature=val)
        elif key == "markup_percent":
            val = float(message.text.replace(",", "."))
            assert 0.0 <= val <= 1000.0
            await db.update_bot_settings(markup_percent=val)
        elif key == "referral_reward_percent":
            val = float(message.text.replace(",", "."))
            assert 0.0 <= val <= 100.0
            await db.update_bot_settings(referral_reward_percent=val)
        elif key in ("referral_bonus", "reffer_bonus"):
            parts = message.text.strip().replace(" ", "").split("-")
            assert len(parts) == 4
            kzt, rub, uah, usd = (float(p.replace(",", ".")) for p in parts)
            await db.update_bot_settings(**{
                f"{key}_kzt": kzt,
                f"{key}_rub": rub,
                f"{key}_uah": uah,
                f"{key}_usd": usd,
            })
        else:
            raise ValueError("Unknown setting")

        try:
            await message.delete()
        except Exception:
            pass

        info = await _admin_panel_text()
        try:
            await bot.edit_message_text(
                chat_id=message.chat.id, message_id=panel_msg_id,
                text=info, parse_mode="Markdown", reply_markup=admin_keyboard(),
            )
        except Exception:
            await message.answer(info, parse_mode="Markdown", reply_markup=admin_keyboard())

    except (ValueError, AssertionError):
        try:
            await message.delete()
        except Exception:
            pass

        bs = await db.get_bot_settings()
        current = _current_value_text(bs, key)
        prompt_text = _SETTING_PROMPTS.get(key, "Введите новое значение:")
        text = f"❌ Некорректное значение.\n\n{prompt_text}\nТекущее значение: `{current}`"

        try:
            await bot.edit_message_text(
                chat_id=message.chat.id, message_id=panel_msg_id,
                text=text, parse_mode="Markdown", reply_markup=_back_kb(),
            )
        except Exception:
            pass
        return

    await state.clear()


# ── Add balance ──────────────────────────────────────────────────

@router.callback_query(F.data == "adm_add_balance")
async def admin_add_balance_prompt(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        return
    text = (
        "💰 *Пополнение баланса пользователя*\n\n"
        "Введите данные в формате:\n"
        "`user_id-сумма`\n\n"
        "Сумма добавляется в валюте пользователя."
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=_back_kb())
    await state.update_data(panel_msg_id=callback.message.message_id)
    await state.set_state(AdminStates.waiting_add_balance)
    await callback.answer()


@router.message(AdminStates.waiting_add_balance, F.text)
async def admin_do_add_balance(message: Message, state: FSMContext, bot: Bot):
    if not _is_admin(message.from_user.id):
        await state.clear()
        return

    data = await state.get_data()
    panel_msg_id = data.get("panel_msg_id")

    try:
        raw = message.text.strip()
        sep = "-" if "-" in raw else " "
        parts = raw.split(sep, 1)
        assert len(parts) == 2
        uid = int(parts[0].strip())
        amount = float(parts[1].strip().replace(",", "."))

        user = await db.get_user(uid)
        if not user:
            raise ValueError("User not found")

        new_bal = await db.add_balance(uid, amount)

        from app.billing import get_currency
        country = user["country"] if user else "Другое"
        cur_code, cur_symbol = get_currency(country)
        await db.create_transaction(
            uid, 7, amount, cur_code, description="Admin top-up",
        )

        try:
            await message.delete()
        except Exception:
            pass

        info = await _admin_panel_text()
        confirm = (
            f"\n\n✅ Баланс `{uid}` пополнен на "
            f"{_fmt(amount)} {cur_symbol}. Новый: {round(new_bal, 2)} {cur_symbol}"
        )
        try:
            await bot.edit_message_text(
                chat_id=message.chat.id, message_id=panel_msg_id,
                text=info + confirm, parse_mode="Markdown", reply_markup=admin_keyboard(),
            )
        except Exception:
            await message.answer(info + confirm, parse_mode="Markdown", reply_markup=admin_keyboard())

    except (ValueError, AssertionError, IndexError):
        try:
            await message.delete()
        except Exception:
            pass

        text = (
            "❌ Некорректный формат.\n\n"
            "Введите данные в формате:\n"
            "`user_id-сумма`"
        )
        try:
            await bot.edit_message_text(
                chat_id=message.chat.id, message_id=panel_msg_id,
                text=text, parse_mode="Markdown", reply_markup=_back_kb(),
            )
        except Exception:
            pass
        return

    await state.clear()


# ── Broadcast ────────────────────────────────────────────────────

@router.callback_query(F.data == "adm_broadcast")
async def admin_broadcast_prompt(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        return
    text = (
        "📢 *Рассылка*\n\n"
        "Отправьте сообщение для рассылки.\n"
        "Поддерживается: текст (Markdown), фото, видео, кружок.\n"
        "Для медиа можно добавить подпись."
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=_back_kb())
    await state.update_data(
        panel_msg_id=callback.message.message_id,
        admin_msg_ids=[], preview_msg_id=None,
    )
    await state.set_state(AdminStates.waiting_broadcast_msg)
    await callback.answer()


@router.message(AdminStates.waiting_broadcast_msg)
async def admin_broadcast_receive(message: Message, state: FSMContext, bot: Bot):
    if not _is_admin(message.from_user.id):
        await state.clear()
        return

    data = await state.get_data()
    panel_msg_id = data.get("panel_msg_id")

    bc_data: dict = {}
    if message.video_note:
        bc_data = {"type": "video_note", "file_id": message.video_note.file_id}
    elif message.photo:
        bc_data = {
            "type": "photo",
            "file_id": message.photo[-1].file_id,
            "caption": message.caption or "",
            "caption_entities": message.caption_entities,
        }
    elif message.video:
        bc_data = {
            "type": "video",
            "file_id": message.video.file_id,
            "caption": message.caption or "",
            "caption_entities": message.caption_entities,
        }
    elif message.text:
        bc_data = {
            "type": "text",
            "text": message.text,
            "entities": message.entities,
        }
    else:
        return

    admin_msg_ids = data.get("admin_msg_ids", [])
    admin_msg_ids.append(message.message_id)

    old_preview = data.get("preview_msg_id")
    if old_preview:
        try:
            await bot.delete_message(message.chat.id, old_preview)
        except Exception:
            pass

    try:
        await bot.edit_message_text(
            chat_id=message.chat.id, message_id=panel_msg_id,
            text="📢 Предпросмотр рассылки:",
        )
    except Exception:
        pass

    preview_msg = await _send_preview(bot, message.chat.id, bc_data)

    await state.update_data(
        broadcast=bc_data,
        admin_msg_ids=admin_msg_ids,
        preview_msg_id=preview_msg.message_id if preview_msg else None,
    )
    await state.set_state(None)


async def _send_preview(bot: Bot, chat_id: int, bc_data: dict) -> Message | None:
    kb = _broadcast_preview_kb()
    try:
        if bc_data["type"] == "text":
            kwargs: dict = {"text": bc_data["text"], "reply_markup": kb}
            if bc_data.get("entities"):
                kwargs["entities"] = bc_data["entities"]
            else:
                kwargs["parse_mode"] = "Markdown"
            return await bot.send_message(chat_id, **kwargs)

        if bc_data["type"] == "photo":
            kwargs = {"photo": bc_data["file_id"], "reply_markup": kb}
            if bc_data.get("caption"):
                kwargs["caption"] = bc_data["caption"]
            if bc_data.get("caption_entities"):
                kwargs["caption_entities"] = bc_data["caption_entities"]
            elif bc_data.get("caption"):
                kwargs["parse_mode"] = "Markdown"
            return await bot.send_photo(chat_id, **kwargs)

        if bc_data["type"] == "video":
            kwargs = {"video": bc_data["file_id"], "reply_markup": kb}
            if bc_data.get("caption"):
                kwargs["caption"] = bc_data["caption"]
            if bc_data.get("caption_entities"):
                kwargs["caption_entities"] = bc_data["caption_entities"]
            elif bc_data.get("caption"):
                kwargs["parse_mode"] = "Markdown"
            return await bot.send_video(chat_id, **kwargs)

        if bc_data["type"] == "video_note":
            return await bot.send_video_note(
                chat_id, video_note=bc_data["file_id"], reply_markup=kb,
            )
    except Exception as e:
        log.error("Broadcast preview error: %s", e)
        try:
            if bc_data["type"] == "text":
                return await bot.send_message(
                    chat_id, bc_data["text"], reply_markup=kb,
                )
        except Exception:
            pass
    return None


# ── Broadcast actions ────────────────────────────────────────────

@router.callback_query(F.data == "adm_bc_send")
async def admin_broadcast_send(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not _is_admin(callback.from_user.id):
        return

    data = await state.get_data()
    bc_data = data.get("broadcast")
    if not bc_data:
        await callback.answer("Нет данных для рассылки", show_alert=True)
        return

    chat_id = callback.message.chat.id
    panel_msg_id = data.get("panel_msg_id")
    preview_msg_id = data.get("preview_msg_id")
    admin_msg_ids = data.get("admin_msg_ids", [])

    for mid in admin_msg_ids:
        try:
            await bot.delete_message(chat_id, mid)
        except Exception:
            pass
    if preview_msg_id:
        try:
            await bot.delete_message(chat_id, preview_msg_id)
        except Exception:
            pass
    if panel_msg_id:
        try:
            await bot.delete_message(chat_id, panel_msg_id)
        except Exception:
            pass

    info = await _admin_panel_text()
    await bot.send_message(chat_id, info, parse_mode="Markdown", reply_markup=admin_keyboard())

    await state.clear()
    await callback.answer("📨 Рассылка запущена...")

    asyncio.create_task(_run_broadcast(bot, chat_id, bc_data))


@router.callback_query(F.data == "adm_bc_edit")
async def admin_broadcast_edit(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not _is_admin(callback.from_user.id):
        return

    data = await state.get_data()
    chat_id = callback.message.chat.id
    panel_msg_id = data.get("panel_msg_id")
    preview_msg_id = data.get("preview_msg_id")
    admin_msg_ids = data.get("admin_msg_ids", [])

    for mid in admin_msg_ids:
        try:
            await bot.delete_message(chat_id, mid)
        except Exception:
            pass
    if preview_msg_id:
        try:
            await bot.delete_message(chat_id, preview_msg_id)
        except Exception:
            pass

    text = (
        "📢 *Рассылка*\n\n"
        "Отправьте сообщение для рассылки.\n"
        "Поддерживается: текст (Markdown), фото, видео, кружок.\n"
        "Для медиа можно добавить подпись."
    )
    try:
        await bot.edit_message_text(
            chat_id=chat_id, message_id=panel_msg_id,
            text=text, parse_mode="Markdown", reply_markup=_back_kb(),
        )
    except Exception:
        new_msg = await bot.send_message(
            chat_id, text, parse_mode="Markdown", reply_markup=_back_kb(),
        )
        await state.update_data(panel_msg_id=new_msg.message_id)

    await state.update_data(
        admin_msg_ids=[], preview_msg_id=None, broadcast=None,
    )
    await state.set_state(AdminStates.waiting_broadcast_msg)
    await callback.answer()


async def _run_broadcast(bot: Bot, admin_chat_id: int, bc_data: dict) -> None:
    try:
        user_ids = await db.get_all_user_ids()
        delivered = 0
        failed = 0

        for uid in user_ids:
            if uid == settings.telegram.admin_id:
                delivered += 1
                continue
            try:
                await _send_bc_to_user(bot, uid, bc_data)
                delivered += 1
            except Exception:
                failed += 1
            await asyncio.sleep(0.05)

        await db.update_bot_settings(blocked_users=failed)

        report = (
            f"📢 *Рассылка завершена*\n\n"
            f"├✅ Доставлено: {delivered}\n"
            f"└❌ Не доставлено: {failed}"
        )
        close_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Закрыть", callback_data="adm_close_report")],
        ])
        await bot.send_message(
            admin_chat_id, report, parse_mode="Markdown", reply_markup=close_kb,
        )
    except Exception as e:
        log.error("Broadcast task error: %s", e)
        try:
            await bot.send_message(admin_chat_id, f"❌ Ошибка рассылки: {e}")
        except Exception:
            pass


async def _send_bc_to_user(bot: Bot, uid: int, bc_data: dict) -> None:
    if bc_data["type"] == "text":
        kwargs: dict = {"text": bc_data["text"]}
        if bc_data.get("entities"):
            kwargs["entities"] = bc_data["entities"]
        else:
            kwargs["parse_mode"] = "Markdown"
        await bot.send_message(uid, **kwargs)

    elif bc_data["type"] == "photo":
        kwargs = {"photo": bc_data["file_id"]}
        if bc_data.get("caption"):
            kwargs["caption"] = bc_data["caption"]
        if bc_data.get("caption_entities"):
            kwargs["caption_entities"] = bc_data["caption_entities"]
        elif bc_data.get("caption"):
            kwargs["parse_mode"] = "Markdown"
        await bot.send_photo(uid, **kwargs)

    elif bc_data["type"] == "video":
        kwargs = {"video": bc_data["file_id"]}
        if bc_data.get("caption"):
            kwargs["caption"] = bc_data["caption"]
        if bc_data.get("caption_entities"):
            kwargs["caption_entities"] = bc_data["caption_entities"]
        elif bc_data.get("caption"):
            kwargs["parse_mode"] = "Markdown"
        await bot.send_video(uid, **kwargs)

    elif bc_data["type"] == "video_note":
        await bot.send_video_note(uid, video_note=bc_data["file_id"])


@router.callback_query(F.data == "adm_close_report")
async def admin_close_report(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        return
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer()
