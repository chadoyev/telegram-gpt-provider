from __future__ import annotations

import asyncio
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app import db
from app.config import settings
from app.handlers import start, chat, menu, admin, payments, image_gen
from app.middlewares import UserRegistrationMiddleware, BotStatusMiddleware, RateLimitMiddleware
from app.webhooks import create_webhook_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("uai_robot")

TELEGRAM_WEBHOOK_PATH = "/tg"


async def on_startup(bot: Bot) -> None:
    webhook_url = f"{settings.webhook_base_url}{TELEGRAM_WEBHOOK_PATH}"
    await bot.set_webhook(
        webhook_url,
        secret_token=settings.webhook_secret,
        drop_pending_updates=True,
    )
    log.info("Telegram webhook set: %s", webhook_url)


async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook()
    log.info("Telegram webhook removed")


async def cleanup_stale_chats(bot: Bot) -> None:
    """Background task: auto-end chats idle for 20+ hours (before Telegram's 24h delete limit)."""
    while True:
        try:
            await asyncio.sleep(600)  # every 10 minutes

            stale = await db.get_stale_active_chats(hours=20)
            if not stale:
                continue

            log.info("Auto-cleanup: found %d stale chats", len(stale))

            for item in stale:
                user_id = item["user_id"]
                chat_id = item["chat_id"]
                try:
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
                        from app.billing import get_currency
                        cur_code, _ = get_currency(country)
                        await db.create_transaction(
                            user_id, 6, total_spent, cur_code,
                            chat_number=chat_id, description="Chat payment (auto)",
                        )

                    user = await db.get_user(user_id)
                    lang = user["language"] or "en" if user else "en"

                    try:
                        from app.chat_export import export_single_chat
                        from aiogram.types import FSInputFile
                        from app.locales import t
                        from app.keyboards import welcome_keyboard, close_keyboard

                        file_path = await export_single_chat(user_id, chat_id, lang)
                        doc = FSInputFile(file_path)
                        await bot.send_document(
                            user_id, doc,
                            caption=t("your_chat_file", lang),
                            reply_markup=close_keyboard(lang),
                        )
                        await bot.send_message(
                            user_id,
                            t("chat_ended", lang),
                            reply_markup=welcome_keyboard(lang),
                        )
                    except Exception as e:
                        log.error("Auto-cleanup export error for user %s: %s", user_id, e)

                    await db.update_user(user_id, status_chat=False)

                except Exception as e:
                    log.error("Auto-cleanup error for user %s chat %s: %s", user_id, chat_id, e)

        except asyncio.CancelledError:
            break
        except Exception as e:
            log.error("Cleanup task error: %s", e)


async def main() -> None:
    await db.create_pool()
    await db.init_schema()
    log.info("Database initialized")

    bot = Bot(
        token=settings.telegram.token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )

    dp = Dispatcher(storage=MemoryStorage())

    rate_limiter = RateLimitMiddleware()
    dp.message.middleware(rate_limiter)
    dp.callback_query.middleware(rate_limiter)
    dp.message.middleware(UserRegistrationMiddleware())
    dp.callback_query.middleware(UserRegistrationMiddleware())
    dp.message.middleware(BotStatusMiddleware())
    dp.callback_query.middleware(BotStatusMiddleware())

    dp.include_routers(
        start.router,
        admin.router,
        image_gen.router,
        payments.router,
        menu.router,
        chat.router,
    )

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = create_webhook_app(bot)

    tg_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.webhook_secret,
    )
    tg_handler.register(app, path=TELEGRAM_WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host=settings.webhook_host, port=settings.webhook_port)
    await site.start()
    log.info(
        "Webhook server started on %s:%s",
        settings.webhook_host,
        settings.webhook_port,
    )

    cleanup_task = asyncio.create_task(cleanup_stale_chats(bot))

    try:
        await asyncio.Event().wait()
    finally:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
        await dp.emit_shutdown()
        await runner.cleanup()
        await db.close_pool()
        await bot.session.close()
        log.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
