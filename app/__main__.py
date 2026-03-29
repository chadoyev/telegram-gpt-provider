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
from app.middlewares import UserRegistrationMiddleware, BotStatusMiddleware
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


async def main() -> None:
    await db.create_pool()
    await db.init_schema()
    log.info("Database initialized")

    bot = Bot(
        token=settings.telegram.token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )

    dp = Dispatcher(storage=MemoryStorage())

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

    try:
        await asyncio.Event().wait()
    finally:
        await dp.emit_shutdown()
        await runner.cleanup()
        await db.close_pool()
        await bot.session.close()
        log.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
