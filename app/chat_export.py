from __future__ import annotations

import html
import logging
from pathlib import Path

from app import db
from app.config import settings
from app.billing import get_currency

log = logging.getLogger(__name__)

LANG_MAP = {"ru": "Русский", "kz": "Казахский", "ua": "Украинский", "en": "Английский"}

_CSS = """
<style>
table { border: 1px solid black; border-collapse: collapse; width: 100%; }
th { background-color: #D3D3D3; border: 1px solid black; padding: 5px; }
td { border: 1px solid black; padding: 5px; vertical-align: top; }
td[rowspan="2"] { white-space: nowrap; width: auto; }
pre { background: #f4f4f4; padding: 8px; border-radius: 4px; overflow-x: auto; }
code { background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }
.current-chat-label { font-size: 20px; font-weight: bold; }
.chat-number { font-size: 20px; font-weight: bold; }
</style>
"""

_LABELS = {
    "ru": {
        "title": "История чатов", "role": "Роли", "messages": "Сообщения",
        "spending": "Траты", "ai": "ИИ:", "user": "Вы:", "chat": "Чат",
        "current_chat": "Текущий чат:",
        "spending_row": "🏷Токены: {tokens_in}/{tokens_out} ~ {tokens_cost} {cur}<br>💸Потрачено: {total} {cur}",
        "total_row": "Итоговые затраты в данном чате:<br>🏷Токены: {tokens_in}/{tokens_out} ~ {tokens_cost} {cur}<br>💸Всего потрачено: {total} {cur}",
    },
    "kz": {
        "title": "Чат тарихы", "role": "Рөлдері", "messages": "Хабарламалар",
        "spending": "Шығындар", "ai": "ИИ:", "user": "Сіз:", "chat": "Чат",
        "current_chat": "Ағымдағы чат:",
        "spending_row": "🏷Токендер: {tokens_in}/{tokens_out} ~ {tokens_cost} {cur}<br>💸Жұмсалған: {total} {cur}",
        "total_row": "Осы чаттағы жалпы шығындар:<br>🏷Токендер: {tokens_in}/{tokens_out} ~ {tokens_cost} {cur}<br>💸Жалпы жұмсалған: {total} {cur}",
    },
    "ua": {
        "title": "Історія чатів", "role": "Ролі", "messages": "Повідомлення",
        "spending": "Витрати", "ai": "ІІ:", "user": "Ви:", "chat": "Чат",
        "current_chat": "Поточний чат:",
        "spending_row": "🏷Токени: {tokens_in}/{tokens_out} ~ {tokens_cost} {cur}<br>💸Витрачено: {total} {cur}",
        "total_row": "Підсумкові витрати у цьому чаті:<br>🏷Токени: {tokens_in}/{tokens_out} ~ {tokens_cost} {cur}<br>💸Усього витрачено: {total} {cur}",
    },
    "en": {
        "title": "Chat History", "role": "Roles", "messages": "Messages",
        "spending": "Spending", "ai": "AI:", "user": "You:", "chat": "Chat",
        "current_chat": "Current chat:",
        "spending_row": "🏷Tokens: {tokens_in}/{tokens_out} ~ {tokens_cost} {cur}<br>💸Spent: {total} {cur}",
        "total_row": "Total costs in this chat:<br>🏷Tokens: {tokens_in}/{tokens_out} ~ {tokens_cost} {cur}<br>💸Total Spent: {total} {cur}",
    },
}

_TX_LABELS = {
    "ru": {
        "title": "Отчет о транзакциях", "name": "Отчет о транзакциях пользователя",
        "date": "Дата операции", "type": "Вид операции", "order": "Ордер платежа",
        "referral": "Реферал", "chat_num": "Номер чата",
        "amount": "Сумма операции", "currency": "Валюта", "status": "Статус операции",
        "types": {
            1: "Пополнение баланса", 2: "Реферальный бонус",
            3: "Кешбек с пополнения реферала", 4: "Конвертация (снятие)",
            5: "Конвертация (зачисление)", 6: "Оплата чата", 7: "Пополнение от админа",
        },
        "success": "Успешно!", "fail": "Не совершена!",
    },
    "kz": {
        "title": "Транзакция туралы есеп", "name": "Пайдаланушы транзакциясы туралы есеп",
        "date": "Транзакция күні", "type": "Операция түрі", "order": "Төлем тәртібі",
        "referral": "Жолдама", "chat_num": "Чат нөмірі",
        "amount": "Транзакция сомасы", "currency": "Валюта", "status": "Жұмыс күйі",
        "types": {
            1: "Балансты толтыру", 2: "Реферал бонусы",
            3: "Реферал толтыру кешбегі", 4: "Айырбастау (алу)",
            5: "Айырбастау (несиелеу)", 6: "Чат төлемі", 7: "Әкімші толтыруы",
        },
        "success": "Сәтті!", "fail": "Аяқталмады!",
    },
    "ua": {
        "title": "Звіт про транзакції", "name": "Звіт про транзакції користувача",
        "date": "Дата операції", "type": "Вид операції", "order": "Ордер платежу",
        "referral": "Реферал", "chat_num": "Номер чату",
        "amount": "Сума операції", "currency": "Валюта", "status": "Статус операції",
        "types": {
            1: "Поповнення балансу", 2: "Реферальний бонус",
            3: "Кешбек з поповнення рефералу", 4: "Конвертація (зняття)",
            5: "Конвертація (зарахування)", 6: "Оплата чату", 7: "Поповнення від адміну",
        },
        "success": "Успішно!", "fail": "Не здійснена!",
    },
    "en": {
        "title": "Transaction Report", "name": "User Transaction Report",
        "date": "Date", "type": "Type", "order": "Payment Order",
        "referral": "Referral", "chat_num": "Chat #",
        "amount": "Amount", "currency": "Currency", "status": "Status",
        "types": {
            1: "Balance top-up", 2: "Referral bonus",
            3: "Referral cashback", 4: "Conversion (withdrawal)",
            5: "Conversion (credit)", 6: "Chat payment", 7: "Admin top-up",
        },
        "success": "Success!", "fail": "Not completed!",
    },
}


def _process_code_blocks(text: str) -> str:
    """Convert markdown code blocks to HTML."""
    if not text:
        return ""
    escaped = html.escape(text)
    result = []
    lines = escaped.split("\n")
    in_code = False
    for line in lines:
        if line.strip().startswith("```"):
            if in_code:
                result.append("</code></pre>")
                in_code = False
            else:
                result.append("<pre><code>")
                in_code = True
        else:
            result.append(line)
    if in_code:
        result.append("</code></pre>")
    return "<br>".join(result) if not any("<pre>" in r for r in result) else "\n".join(result)


def _parse_spending(spending: str) -> dict:
    """Parse the spending string: tokens_in~tokens_out~cost~balance~model"""
    parts = spending.split("~") if spending else []
    return {
        "tokens_in": parts[0] if len(parts) > 0 else "0",
        "tokens_out": parts[1] if len(parts) > 1 else "0",
        "cost": float(parts[2]) if len(parts) > 2 else 0.0,
        "balance": float(parts[3]) if len(parts) > 3 else 0.0,
        "model": parts[4] if len(parts) > 4 else "",
    }


def _ensure_dir(user_id: int) -> Path:
    d = Path(settings.messages_dir) / str(user_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


async def export_single_chat(user_id: int, chat_id: int, lang: str = "en") -> str:
    """Generate an HTML file for a single chat. Returns file path."""
    labels = _LABELS.get(lang, _LABELS["en"])
    user = await db.get_user(user_id)
    _, cur_symbol = get_currency(user["country"] if user else None)
    messages = await db.get_chat_messages(user_id, chat_id)

    total_cost = 0.0
    total_tokens_in = 0
    total_tokens_out = 0

    rows_html = ""
    i = 0
    while i < len(messages):
        msg = messages[i]
        role_label = labels["user"] if msg["role"] == "user" else labels["ai"]
        content = _process_code_blocks(msg["content"] or "")

        sp = _parse_spending(msg.get("spending", "") or "")
        spending_html = ""
        if sp["cost"] > 0:
            total_cost += sp["cost"]
            try:
                total_tokens_in += int(float(sp["tokens_in"]))
                total_tokens_out += int(float(sp["tokens_out"]))
            except ValueError:
                pass
            spending_html = labels["spending_row"].format(
                tokens_in=sp["tokens_in"], tokens_out=sp["tokens_out"],
                tokens_cost=round(sp["cost"], 4), cur=cur_symbol, total=round(sp["cost"], 4),
            )
            if sp["model"]:
                spending_html = f"🤖{sp['model']}<br>{spending_html}"

        if msg["role"] == "user":
            next_msg = messages[i + 1] if i + 1 < len(messages) and messages[i + 1]["role"] == "assistant" else None
            if next_msg:
                ai_content = _process_code_blocks(next_msg["content"] or "")
                ai_sp = _parse_spending(next_msg.get("spending", "") or "")
                if ai_sp["cost"] > 0:
                    total_cost += ai_sp["cost"]
                    try:
                        total_tokens_in += int(float(ai_sp["tokens_in"]))
                        total_tokens_out += int(float(ai_sp["tokens_out"]))
                    except ValueError:
                        pass
                    spending_html = labels["spending_row"].format(
                        tokens_in=ai_sp["tokens_in"], tokens_out=ai_sp["tokens_out"],
                        tokens_cost=round(ai_sp["cost"], 4), cur=cur_symbol, total=round(ai_sp["cost"], 4),
                    )
                    if ai_sp["model"]:
                        spending_html = f"🤖{ai_sp['model']}<br>{spending_html}"

                rows_html += f"""
                <tr>
                    <td>{labels['user']}</td>
                    <td>{content}</td>
                    <td rowspan="2">{spending_html}</td>
                </tr>
                <tr>
                    <td>{labels['ai']}</td>
                    <td>{ai_content}</td>
                </tr>"""
                i += 2
                continue

        rows_html += f"""
        <tr>
            <td>{role_label}</td>
            <td>{content}</td>
            <td>{spending_html or '-'}</td>
        </tr>"""
        i += 1

    total_html = labels["total_row"].format(
        tokens_in=total_tokens_in, tokens_out=total_tokens_out,
        tokens_cost=round(total_cost, 4), cur=cur_symbol, total=round(total_cost, 4),
    )

    doc = f"""<html>
<head><meta charset="UTF-8"><title>{labels['title']}</title>{_CSS}</head>
<body>
<h1>{labels['title']} #{chat_id}</h1>
<table>
<tr><th>{labels['role']}</th><th>{labels['messages']}</th><th>{labels['spending']}</th></tr>
{rows_html}
<tr><td colspan="3">{total_html}</td></tr>
</table>
</body></html>"""

    out_dir = _ensure_dir(user_id)
    path = out_dir / f"chat_history{user_id}-{chat_id}.html"
    path.write_text(doc, encoding="utf-8")
    return str(path)


async def export_all_chats(user_id: int, lang: str = "en") -> str:
    """Generate an HTML file with all closed chats (with JS tabs). Returns file path."""
    labels = _LABELS.get(lang, _LABELS["en"])
    user = await db.get_user(user_id)
    _, cur_symbol = get_currency(user["country"] if user else None)
    chat_ids = await db.get_all_chat_ids(user_id, closed_only=True)

    buttons_html = "   ".join(
        f'<button onclick="show_chat({cid})">{labels["chat"]} {cid}</button>' for cid in chat_ids
    )

    chats_html = ""
    for cid in chat_ids:
        messages = await db.get_chat_messages(user_id, cid)
        total_cost = 0.0
        total_tokens_in = 0
        total_tokens_out = 0

        rows = ""
        i = 0
        while i < len(messages):
            msg = messages[i]
            content = _process_code_blocks(msg["content"] or "")
            sp = _parse_spending(msg.get("spending", "") or "")
            spending_html = ""

            if msg["role"] == "user":
                nxt = messages[i + 1] if i + 1 < len(messages) and messages[i + 1]["role"] == "assistant" else None
                if nxt:
                    ai_content = _process_code_blocks(nxt["content"] or "")
                    ai_sp = _parse_spending(nxt.get("spending", "") or "")
                    if ai_sp["cost"] > 0:
                        total_cost += ai_sp["cost"]
                        try:
                            total_tokens_in += int(float(ai_sp["tokens_in"]))
                            total_tokens_out += int(float(ai_sp["tokens_out"]))
                        except ValueError:
                            pass
                        spending_html = labels["spending_row"].format(
                            tokens_in=ai_sp["tokens_in"], tokens_out=ai_sp["tokens_out"],
                            tokens_cost=round(ai_sp["cost"], 4), cur=cur_symbol, total=round(ai_sp["cost"], 4),
                        )
                        if ai_sp["model"]:
                            spending_html = f"🤖{ai_sp['model']}<br>{spending_html}"
                    rows += f"""<tr><td>{labels['user']}</td><td>{content}</td>
                        <td rowspan="2">{spending_html}</td></tr>
                        <tr><td>{labels['ai']}</td><td>{ai_content}</td></tr>"""
                    i += 2
                    continue

            role_label = labels["user"] if msg["role"] == "user" else labels["ai"]
            rows += f"<tr><td>{role_label}</td><td>{content}</td><td>-</td></tr>"
            i += 1

        total_html = labels["total_row"].format(
            tokens_in=total_tokens_in, tokens_out=total_tokens_out,
            tokens_cost=round(total_cost, 4), cur=cur_symbol, total=round(total_cost, 4),
        )
        chats_html += f"""
        <table class="chat" id="chat-{cid}" style="display:none">
        <tr><th>{labels['role']}</th><th>{labels['messages']}</th><th>{labels['spending']}</th></tr>
        {rows}
        <tr><td colspan="3">{total_html}</td></tr>
        </table>"""

    js = """<script>
function show_chat(id_chat) {
    var chats = document.getElementsByClassName('chat');
    for (var i = 0; i < chats.length; i++) { chats[i].style.display = 'none'; }
    var chat = document.getElementById('chat-' + id_chat);
    if (chat) chat.style.display = 'table';
    var cn = document.getElementById('chat-number');
    cn.innerHTML = '<span class="current-chat-label">""" + labels["current_chat"] + """ </span><span class="chat-number">' + id_chat + '</span>';
}
</script>"""

    doc = f"""<html>
<head><meta charset="UTF-8"><title>{labels['title']}</title>{_CSS}{js}</head>
<body>
<h1>{labels['title']}</h1>
{buttons_html}
<div id="chat-number"></div>
{chats_html}
</body></html>"""

    out_dir = _ensure_dir(user_id)
    path = out_dir / f"chats_history{user_id}.html"
    path.write_text(doc, encoding="utf-8")
    return str(path)


async def export_transactions(user_id: int, lang: str = "en") -> str:
    """Generate an HTML file for all transactions. Returns file path."""
    labels = _TX_LABELS.get(lang, _TX_LABELS["en"])
    txs = await db.get_user_transactions(user_id)

    rows_html = ""
    for tx in txs:
        tx_type = labels["types"].get(tx["type"], str(tx["type"]))
        status_text = labels["success"] if tx["status"] else labels["fail"]
        dt = tx["created_at"].strftime("%d.%m.%Y %H:%M") if tx["created_at"] else ""
        ref = str(tx["referral_id"] or "-")
        cn = str(tx["chat_number"] or "-")
        rows_html += f"""<tr>
            <td>{dt}</td><td>{tx_type}</td>
            <td>{tx['merchant_order_id'] or '-'}</td>
            <td>{ref}</td><td>{cn}</td>
            <td>{tx['amount']}</td><td>{tx['currency']}</td>
            <td>{status_text}</td>
        </tr>"""

    doc = f"""<html>
<head><meta charset="UTF-8"><title>{labels['title']}</title>
<style>
table {{ border: 1px solid black; border-collapse: collapse; }}
th {{ background-color: #D3D3D3; border: 1px solid black; padding: 5px; }}
td {{ border: 1px solid black; padding: 5px; }}
</style>
</head>
<body>
<h1>{labels['name']} {user_id}</h1>
<table>
<tr>
<th>{labels['date']}</th><th>{labels['type']}</th><th>{labels['order']}</th>
<th>{labels['referral']}</th><th>{labels['chat_num']}</th>
<th>{labels['amount']}</th><th>{labels['currency']}</th><th>{labels['status']}</th>
</tr>
{rows_html}
</table>
</body></html>"""

    out_dir = _ensure_dir(user_id)
    path = out_dir / f"transaction_report_{user_id}.html"
    path.write_text(doc, encoding="utf-8")
    return str(path)
