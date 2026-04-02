from __future__ import annotations

import logging
import time
from collections import defaultdict
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


class RateLimitMiddleware(BaseMiddleware):
    """DDoS protection: ban user for 24h if they flood the bot."""

    WINDOW = 10
    MAX_MESSAGES = 15
    BAN_DURATION = 86400

    def __init__(self):
        self._timestamps: dict[int, list[float]] = defaultdict(list)
        self._banned: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_obj = None
        if isinstance(event, Message) and event.from_user:
            user_obj = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_obj = event.from_user

        if not user_obj:
            return await handler(event, data)

        user_id = user_obj.id
        if user_id == settings.telegram.admin_id:
            return await handler(event, data)

        now = time.monotonic()

        if user_id in self._banned:
            if now - self._banned[user_id] < self.BAN_DURATION:
                return
            del self._banned[user_id]

        timestamps = self._timestamps[user_id]
        timestamps.append(now)
        cutoff = now - self.WINDOW
        self._timestamps[user_id] = [ts for ts in timestamps if ts > cutoff]

        if len(self._timestamps[user_id]) > self.MAX_MESSAGES:
            self._banned[user_id] = now
            self._timestamps.pop(user_id, None)
            log.warning("Rate limit ban: user %s blocked for 24h", user_id)

            if isinstance(event, Message):
                try:
                    from app.locales import t
                    lang = data.get("lang", "en")
                    await event.answer(t("rate_limit_banned", lang))
                except Exception:
                    pass
            elif isinstance(event, CallbackQuery):
                try:
                    from app.locales import t
                    lang = data.get("lang", "en")
                    await event.answer(t("rate_limit_banned", lang), show_alert=True)
                except Exception:
                    pass
            return

        return await handler(event, data)
