from __future__ import annotations

import asyncio
import logging
import ssl

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode  # noqa: F401
from aiogram.fsm.storage.memory import MemoryStorage

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

    webhook_app = create_webhook_app(bot)

    runner = web.AppRunner(webhook_app)
    await runner.setup()

    ssl_context = None
    if settings.ssl_cert and settings.ssl_key:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(settings.ssl_cert, settings.ssl_key)

    site = web.TCPSite(
        runner,
        host=settings.webhook_host,
        port=settings.webhook_port,
        ssl_context=ssl_context,
    )
    await site.start()
    log.info(
        "Payment webhook server started on %s:%s (SSL: %s)",
        settings.webhook_host,
        settings.webhook_port,
        bool(ssl_context),
    )

    log.info("Bot starting polling...")
    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()
        await db.close_pool()
        await bot.session.close()
        log.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
