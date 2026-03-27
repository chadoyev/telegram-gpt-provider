from __future__ import annotations

import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app import db
from app.billing import charge_image, check_balance, get_currency
from app.keyboards import welcome_keyboard, close_keyboard
from app.locales import t
from app.openai_client import generate_image

log = logging.getLogger(__name__)
router = Router(name="image_gen")


class ImageStates(StatesGroup):
    waiting_prompt = State()


@router.callback_query(F.data == "gen_image")
async def start_image_gen(callback: CallbackQuery, state: FSMContext, lang: str = "en"):
    user = await db.get_user(callback.from_user.id)
    if user and user["status_chat"]:
        await callback.answer(t("already_has_chat", lang), show_alert=True)
        return

    await callback.message.edit_text(t("img_gen_prompt", lang))
    await state.set_state(ImageStates.waiting_prompt)
    await callback.answer()


@router.message(ImageStates.waiting_prompt)
async def do_generate_image(message: Message, state: FSMContext, bot: Bot, db_user=None, lang: str = "en"):
    if not db_user or not message.text:
        await state.clear()
        return

    user_id = message.from_user.id
    country = db_user["country"]

    if not await check_balance(user_id, 0.04, country):
        await message.answer(t("insufficient_funds", lang))
        await state.clear()
        return

    status_msg = await message.answer(t("img_generating", lang))

    try:
        image_url = await generate_image(message.text)
    except Exception as e:
        log.error("DALL-E error: %s", e)
        await status_msg.edit_text(t("unexpected_error", lang))
        await state.clear()
        return

        cost_local, new_balance = await charge_image(user_id, country)
    _, cur = get_currency(country)

    caption = t(
        "img_ready", lang,
        prompt=message.text[:100],
        cost=round(cost_local, 4),
        balance=round(new_balance, 2),
        cur=cur,
    )

    try:
        await status_msg.delete()
    except Exception:
        pass

    await message.answer_photo(
        photo=image_url,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=close_keyboard(lang),
    )

    await message.answer(
        t("welcome_message", lang),
        parse_mode="Markdown",
        reply_markup=welcome_keyboard(lang),
    )
    await state.clear()
