from __future__ import annotations

import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app import db
from app.config import settings
from app.locales import t

log = logging.getLogger(__name__)
router = Router(name="admin")


class AdminStates(StatesGroup):
    waiting_broadcast = State()
    waiting_add_balance_user = State()
    waiting_add_balance_amount = State()
    waiting_setting_value = State()


def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_refresh")],
        [InlineKeyboardButton(text="⚡ Статус бота", callback_data="admin_toggle_status")],
        [InlineKeyboardButton(text="🌡 Температура", callback_data="admin_temperature")],
        [InlineKeyboardButton(text="📝 Max токенов", callback_data="admin_max_tokens")],
        [InlineKeyboardButton(text="💰 Пополнить баланс юзера", callback_data="admin_add_balance")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
    ])


def _is_admin(user_id: int) -> bool:
    return user_id == settings.telegram.admin_id


async def _admin_panel_text() -> str:
    bs = await db.get_bot_settings()
    users_count = await db.count_users()
    return (
        f"*Админ-панель*\n"
        f"Статус бота: {'✅' if bs['status'] else '❌'}\n"
        f"Пользователей: {users_count}\n"
        f"Температура: {bs['temperature']}\n"
        f"Max токенов: {bs['max_tokens']}"
    )


async def try_admin_command(message: Message) -> bool:
    """Called from the text handler. Returns True if this was an admin trigger."""
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


@router.callback_query(F.data == "admin_refresh")
async def admin_refresh(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        return
    info = await _admin_panel_text()
    await callback.message.edit_text(info, parse_mode="Markdown", reply_markup=admin_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin_toggle_status")
async def toggle_status(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        return
    bs = await db.get_bot_settings()
    new_status = not bs["status"]
    await db.update_bot_settings(status=new_status)
    await callback.answer(f"Бот {'включён' if new_status else 'выключен'}", show_alert=True)
    info = await _admin_panel_text()
    await callback.message.edit_text(info, parse_mode="Markdown", reply_markup=admin_keyboard())


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        return
    users = await db.count_users()
    await callback.message.edit_text(
        f"*Статистика*\nВсего пользователей: {users}",
        parse_mode="Markdown",
        reply_markup=admin_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        return
    await callback.message.answer(t("admin_broadcast_prompt", "ru"))
    await state.set_state(AdminStates.waiting_broadcast)
    await callback.answer()


@router.message(AdminStates.waiting_broadcast)
async def do_broadcast(message: Message, state: FSMContext, bot: Bot):
    if not _is_admin(message.from_user.id):
        await state.clear()
        return

    user_ids = await db.get_all_user_ids()
    count = 0
    for uid in user_ids:
        try:
            await bot.send_message(uid, message.text)
            count += 1
        except Exception:
            pass

    await message.answer(t("admin_broadcast_done", "ru", count=count))
    await state.clear()


@router.callback_query(F.data == "admin_add_balance")
async def admin_add_balance(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        return
    await callback.message.answer("Введите user_id пользователя:")
    await state.set_state(AdminStates.waiting_add_balance_user)
    await callback.answer()


@router.message(AdminStates.waiting_add_balance_user)
async def admin_balance_user(message: Message, state: FSMContext):
    try:
        uid = int(message.text)
        user = await db.get_user(uid)
        if not user:
            await message.answer("Пользователь не найден.")
            await state.clear()
            return
        await state.update_data(target_user=uid)
        await message.answer(f"Пользователь: {user['user_name']} ({uid})\nВведите сумму:")
        await state.set_state(AdminStates.waiting_add_balance_amount)
    except ValueError:
        await message.answer("Некорректный ID.")
        await state.clear()


@router.message(AdminStates.waiting_add_balance_amount)
async def admin_balance_amount(message: Message, state: FSMContext):
    data = await state.get_data()
    uid = data.get("target_user")
    try:
        amount = float(message.text)
        new_bal = await db.add_balance(uid, amount)

        user = await db.get_user(uid)
        country = user["country"] if user else "Другое"
        cur_code, _ = get_currency_for_admin(country)
        await db.create_transaction(
            uid, 7, amount, cur_code,
            description="Admin top-up",
        )

        await message.answer(f"✅ Баланс пополнен. Новый баланс: {round(new_bal, 2)}")
    except (ValueError, TypeError):
        await message.answer("Некорректная сумма.")
    await state.clear()


@router.callback_query(F.data == "admin_temperature")
async def admin_temp(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        return
    await callback.message.answer("Введите новое значение температуры (0.0 — 2.0):")
    await state.update_data(setting_key="temperature")
    await state.set_state(AdminStates.waiting_setting_value)
    await callback.answer()


@router.callback_query(F.data == "admin_max_tokens")
async def admin_tokens(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        return
    await callback.message.answer("Введите новое максимальное количество токенов (1 — 16384):")
    await state.update_data(setting_key="max_tokens")
    await state.set_state(AdminStates.waiting_setting_value)
    await callback.answer()


@router.message(AdminStates.waiting_setting_value)
async def set_setting_value(message: Message, state: FSMContext):
    data = await state.get_data()
    key = data.get("setting_key")
    try:
        if key == "temperature":
            val = float(message.text)
            assert 0.0 <= val <= 2.0
            await db.update_bot_settings(temperature=val)
        elif key == "max_tokens":
            val = int(message.text)
            assert 1 <= val <= 16384
            await db.update_bot_settings(max_tokens=val)
        await message.answer(f"✅ {key} обновлён: {val}")
    except (ValueError, AssertionError):
        await message.answer("Некорректное значение.")
    await state.clear()


def get_currency_for_admin(country: str) -> tuple[str, str]:
    from app.billing import get_currency
    return get_currency(country)
