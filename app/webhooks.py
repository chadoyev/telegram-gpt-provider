from __future__ import annotations

import hashlib
import logging

from aiohttp import web

from app import db
from app.billing import get_currency
from app.config import settings

log = logging.getLogger(__name__)

routes = web.RouteTableDef()


def _md5(*args: str) -> str:
    return hashlib.md5(":".join(str(a) for a in args).encode()).hexdigest()


@routes.get("/health")
async def health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


@routes.get("/robokassa")
async def robokassa_webhook(request: web.Request) -> web.Response:
    """Robokassa result URL (GET) — used for KZ, UA, Other countries."""
    try:
        data = request.query
        out_sum = data.get("OutSum", "0")
        inv_id = data.get("InvId", "")
        shp_id = data.get("Shp_id", "")
        received_sign = data.get("SignatureValue", "")

        expected_sign = _md5(out_sum, inv_id, settings.robokassa.pass2, f"Shp_id={shp_id}")

        if received_sign.lower() != expected_sign.lower():
            log.warning("Robokassa invalid signature for inv %s", inv_id)
            return web.Response(text="bad sign", status=400)

        user_id = int(shp_id)
        order_id = f"{shp_id}-{inv_id}"
        amount = await db.get_transaction_amount(order_id)
        if amount is None:
            log.warning("Robokassa order not found: %s", order_id)
            return web.Response(text="order not found", status=400)

        await db.update_transaction_status(order_id, True)
        user = await db.get_user(user_id)
        country = user["country"] if user else "Другое"
        _, cur_symbol = get_currency(country)

        await db.add_balance(user_id, amount)

        referrer_id = user["reffer"] if user else 0
        if referrer_id and referrer_id != 0:
            await _process_cashback(referrer_id, user_id, amount, country)

        bot = request.app.get("bot")
        if bot:
            try:
                from app.locales import t
                lang = user["language"] or "en" if user else "en"
                await bot.send_message(
                    user_id,
                    f"✅{t('pay_success', lang, amount=amount, cur=cur_symbol)}\n"
                    f"├Ордер: {order_id}\n└Сумма: {amount} {cur_symbol}",
                )
            except Exception:
                pass

        log.info("Robokassa payment OK: user=%s amount=%s", user_id, amount)
        return web.Response(text=f"OK{inv_id}")

    except Exception as e:
        log.error("Robokassa webhook error: %s", e)
        return web.Response(text="ERR", status=500)


@routes.post("/yookassa")
async def yookassa_webhook(request: web.Request) -> web.Response:
    """YooKassa webhook (POST JSON) — used for Russia."""
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
        order_id_part = metadata.get("order_id", "")

        if not user_id:
            return web.json_response({"status": "no user_id"})

        order_id = f"{user_id}-{order_id_part}"
        stored_amount = await db.get_transaction_amount(order_id)
        if stored_amount is not None:
            actual_amount = stored_amount
        else:
            actual_amount = amount

        await db.update_transaction_status(order_id, True)
        await db.add_balance(user_id, actual_amount)

        user = await db.get_user(user_id)
        referrer_id = user["reffer"] if user else 0
        if referrer_id and referrer_id != 0:
            await _process_cashback(referrer_id, user_id, actual_amount, "Россия")

        bot = request.app.get("bot")
        if bot:
            try:
                from app.locales import t
                lang = user["language"] or "en" if user else "en"
                await bot.send_message(
                    user_id,
                    f"✅{t('pay_success', lang, amount=actual_amount, cur='₽')}\n"
                    f"├Ордер: {order_id}\n└Сумма: {actual_amount} ₽",
                )
            except Exception:
                pass

        log.info("YooKassa payment OK: user=%s amount=%s %s", user_id, actual_amount, currency)
        return web.json_response({"status": "ok"})

    except Exception as e:
        log.error("YooKassa webhook error: %s", e)
        return web.json_response({"status": "error"}, status=500)


async def _process_cashback(referrer_id: int, payer_id: int, amount: float, payer_country: str):
    """Credit cashback to referrer when their referral makes a payment."""
    try:
        bs = await db.get_bot_settings()
        cashback_pct = int(bs["cashback"])
        if cashback_pct <= 0:
            return

        bonus = round((amount * cashback_pct) / 100)
        if bonus <= 0:
            return

        referrer = await db.get_user(referrer_id)
        if not referrer:
            return

        referrer_country = referrer["country"]
        _, payer_cur_code = get_currency(payer_country)
        ref_cur_code, ref_cur_symbol = get_currency(referrer_country)

        if payer_country != referrer_country:
            from app.billing import get_exchange_rate
            payer_rate = await get_exchange_rate(payer_country)
            ref_rate = await get_exchange_rate(referrer_country)
            if payer_rate > 0:
                bonus_usd = bonus / payer_rate
                bonus = round(bonus_usd * ref_rate, 2)

        await db.add_balance(referrer_id, bonus)
        await db.create_transaction(
            referrer_id, 3, bonus, ref_cur_code,
            description="Cashback", referral_id=payer_id,
        )
    except Exception as e:
        log.error("Cashback error: %s", e)


def create_webhook_app(bot=None) -> web.Application:
    app = web.Application()
    app.add_routes(routes)
    if bot:
        app["bot"] = bot
    return app
