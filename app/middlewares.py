from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from app import db
from app.config import settings

log = logging.getLogger(__name__)


class UserRegistrationMiddleware(BaseMiddleware):
    """Ensure user exists in DB before any handler runs."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = None
        if isinstance(event, Message) and event.from_user:
            user = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            user = event.from_user

        if user:
            db_user = await db.get_user(user.id)
            if db_user:
                data["db_user"] = db_user
                data["lang"] = db_user["language"] or "en"
            else:
                data["db_user"] = None
                data["lang"] = "en"

        return await handler(event, data)


class BotStatusMiddleware(BaseMiddleware):
    """Check if bot is enabled before processing messages."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            if event.from_user.id == settings.telegram.admin_id:
                return await handler(event, data)

        if isinstance(event, CallbackQuery) and event.from_user:
            if event.from_user.id == settings.telegram.admin_id:
                return await handler(event, data)

        bs = await db.get_bot_settings()
        if bs and not bs["status"]:
            from app.locales import t
            lang = data.get("lang", "en")
            if isinstance(event, Message):
                await event.answer(t("bot_unavailable", lang))
                return
            elif isinstance(event, CallbackQuery):
                await event.answer(t("bot_unavailable", lang), show_alert=True)
                return
        return await handler(event, data)
