from __future__ import annotations

import hashlib
import logging

from aiohttp import web

from app import db
from app.billing import get_currency
from app.config import settings

log = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.get("/health")
async def health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


@routes.post("/freekassa")
async def freekassa_webhook(request: web.Request) -> web.Response:
    try:
        data = await request.post()
        merchant_id = data.get("MERCHANT_ID", "")
        amount = data.get("AMOUNT", "0")
        order_id = data.get("MERCHANT_ORDER_ID", "")
        sign = data.get("SIGN", "")

        expected_sign = hashlib.md5(
            f"{merchant_id}:{amount}:{settings.freekassa.secret2}:{order_id}".encode()
        ).hexdigest()

        if sign != expected_sign:
            log.warning("FreeKassa invalid signature for order %s", order_id)
            return web.Response(text="ERR", status=400)

        parts = order_id.split("_")
        user_id = int(parts[0])
        local_amount = float(amount)

        await db.add_balance(user_id, local_amount)
        await db.create_transaction(
            user_id=user_id, tx_type=1, amount=local_amount,
            currency="RUB", merchant_order_id=order_id,
            description="FreeKassa payment",
        )

        bot = request.app.get("bot")
        if bot:
            _, cur = get_currency("Россия")
            try:
                await bot.send_message(
                    user_id,
                    f"✅ Баланс пополнен на {local_amount} {cur}!"
                )
            except Exception:
                pass

        log.info("FreeKassa payment OK: user=%s amount=%s", user_id, local_amount)
        return web.Response(text="YES")

    except Exception as e:
        log.error("FreeKassa webhook error: %s", e)
        return web.Response(text="ERR", status=500)


@routes.post("/robokassa")
async def robokassa_webhook(request: web.Request) -> web.Response:
    try:
        data = await request.post()
        out_sum = data.get("OutSum", "0")
        inv_id = data.get("InvId", "")
        sign = data.get("SignatureValue", "")

        expected_sign = hashlib.md5(
            f"{out_sum}:{inv_id}:{settings.robokassa.pass2}".encode()
        ).hexdigest().upper()

        if sign.upper() != expected_sign:
            log.warning("Robokassa invalid signature for inv %s", inv_id)
            return web.Response(text="ERR", status=400)

        parts = inv_id.split("_") if "_" in str(inv_id) else [inv_id]
        user_id = int(parts[0])
        local_amount = float(out_sum)

        await db.add_balance(user_id, local_amount)
        await db.create_transaction(
            user_id=user_id, tx_type=2, amount=local_amount,
            currency="RUB", merchant_order_id=str(inv_id),
            description="Robokassa payment",
        )

        bot = request.app.get("bot")
        if bot:
            try:
                await bot.send_message(user_id, f"✅ Баланс пополнен на {local_amount}!")
            except Exception:
                pass

        log.info("Robokassa payment OK: user=%s amount=%s", user_id, local_amount)
        return web.Response(text=f"OK{inv_id}")

    except Exception as e:
        log.error("Robokassa webhook error: %s", e)
        return web.Response(text="ERR", status=500)


@routes.post("/yookassa")
async def yookassa_webhook(request: web.Request) -> web.Response:
    try:
        body = await request.json()
        event_type = body.get("event", "")

        if event_type != "payment.succeeded":
            return web.json_response({"status": "ignored"})

        payment = body.get("object", {})
        amount = float(payment.get("amount", {}).get("value", 0))
        currency = payment.get("amount", {}).get("currency", "RUB")
        metadata = payment.get("metadata", {})
        user_id = int(metadata.get("user_id", 0))
        order_id = payment.get("id", "")

        if not user_id:
            return web.json_response({"status": "no user_id"})

        await db.add_balance(user_id, amount)
        await db.create_transaction(
            user_id=user_id, tx_type=3, amount=amount,
            currency=currency, merchant_order_id=order_id,
            description="YooKassa payment",
        )

        bot = request.app.get("bot")
        if bot:
            try:
                await bot.send_message(user_id, f"✅ Баланс пополнен на {amount} {currency}!")
            except Exception:
                pass

        log.info("YooKassa payment OK: user=%s amount=%s %s", user_id, amount, currency)
        return web.json_response({"status": "ok"})

    except Exception as e:
        log.error("YooKassa webhook error: %s", e)
        return web.json_response({"status": "error"}, status=500)


def create_webhook_app(bot=None) -> web.Application:
    app = web.Application()
    app.add_routes(routes)
    if bot:
        app["bot"] = bot
    return app
