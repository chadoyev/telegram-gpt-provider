from __future__ import annotations

import base64
import html
import logging
import mimetypes
from pathlib import Path

from app import db
from app.config import settings
from app.billing import get_currency

log = logging.getLogger(__name__)

LANG_MAP = {"ru": "Русский", "kz": "Казахский", "ua": "Украинский", "en": "Английский"}

_CSS = """<style>
*{box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;margin:20px;background:#fafafa;color:#222}
h1{color:#333}
table{border:1px solid #d0d0d0;border-collapse:collapse;width:100%;background:#fff;margin-bottom:20px}
th{background:#e8e8e8;border:1px solid #d0d0d0;padding:8px;text-align:left}
td{border:1px solid #d0d0d0;padding:8px;vertical-align:top}
td[rowspan="2"]{white-space:nowrap;width:auto}
pre{background:#f4f4f4;padding:8px;border-radius:4px;overflow-x:auto}
code{background:#f4f4f4;padding:2px 4px;border-radius:3px}
.current-chat-label{font-size:20px;font-weight:bold}
.chat-number{font-size:20px;font-weight:bold}
audio{max-width:300px;display:block;margin:4px 0}
.media-img{max-width:400px;border-radius:8px;display:block;margin:4px 0}
.download-btn{display:inline-block;margin:4px 0;padding:5px 14px;background:#4CAF50;color:#fff;
  border:none;border-radius:4px;cursor:pointer;font-size:13px;text-decoration:none}
.download-btn:hover{background:#45a049}
.doc-attachment{display:inline-flex;align-items:center;gap:8px;padding:6px 10px;background:#f3f3f3;
  border-radius:6px;border:1px solid #e0e0e0;margin:4px 0}
button.tab-btn{margin:2px;padding:6px 14px;cursor:pointer;border:1px solid #ccc;border-radius:4px;background:#fff}
button.tab-btn:hover{background:#e8e8e8}
</style>"""

_DOWNLOAD_JS = """<script>
var fileData={};
function downloadFile(fid,fname,mime){
  var b64=fileData[fid];if(!b64)return;
  var bc=atob(b64),bn=new Uint8Array(bc.length);
  for(var i=0;i<bc.length;i++)bn[i]=bc.charCodeAt(i);
  var blob=new Blob([bn],{type:mime}),url=URL.createObjectURL(blob);
  var a=document.createElement('a');a.href=url;a.download=fname;
  document.body.appendChild(a);a.click();document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
function downloadFromImg(imgId,fname,mime){
  var img=document.getElementById(imgId);if(!img)return;
  var b64=img.src.split(',')[1];if(!b64)return;
  var bc=atob(b64),bn=new Uint8Array(bc.length);
  for(var i=0;i<bc.length;i++)bn[i]=bc.charCodeAt(i);
  var blob=new Blob([bn],{type:mime}),url=URL.createObjectURL(blob);
  var a=document.createElement('a');a.href=url;a.download=fname;
  document.body.appendChild(a);a.click();document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
</script>"""

_LABELS = {
    "ru": {
        "title": "История чатов", "role": "Роли", "messages": "Сообщения",
        "spending": "Траты", "ai": "ИИ:", "user": "Вы:", "chat": "Чат",
        "current_chat": "Текущий чат:", "download": "Скачать",
        "spending_row": "🏷Токены: {tokens_in}/{tokens_out} ~ {tokens_cost} {cur}<br>💸Потрачено: {total} {cur}",
        "total_row": "Итоговые затраты в данном чате:<br>🏷Токены: {tokens_in}/{tokens_out} ~ {tokens_cost} {cur}<br>💸Всего потрачено: {total} {cur}",
    },
    "kz": {
        "title": "Чат тарихы", "role": "Рөлдері", "messages": "Хабарламалар",
        "spending": "Шығындар", "ai": "ИИ:", "user": "Сіз:", "chat": "Чат",
        "current_chat": "Ағымдағы чат:", "download": "Жүктеу",
        "spending_row": "🏷Токендер: {tokens_in}/{tokens_out} ~ {tokens_cost} {cur}<br>💸Жұмсалған: {total} {cur}",
        "total_row": "Осы чаттағы жалпы шығындар:<br>🏷Токендер: {tokens_in}/{tokens_out} ~ {tokens_cost} {cur}<br>💸Жалпы жұмсалған: {total} {cur}",
    },
    "ua": {
        "title": "Історія чатів", "role": "Ролі", "messages": "Повідомлення",
        "spending": "Витрати", "ai": "ІІ:", "user": "Ви:", "chat": "Чат",
        "current_chat": "Поточний чат:", "download": "Завантажити",
        "spending_row": "🏷Токени: {tokens_in}/{tokens_out} ~ {tokens_cost} {cur}<br>💸Витрачено: {total} {cur}",
        "total_row": "Підсумкові витрати у цьому чаті:<br>🏷Токени: {tokens_in}/{tokens_out} ~ {tokens_cost} {cur}<br>💸Усього витрачено: {total} {cur}",
    },
    "en": {
        "title": "Chat History", "role": "Roles", "messages": "Messages",
        "spending": "Spending", "ai": "AI:", "user": "You:", "chat": "Chat",
        "current_chat": "Current chat:", "download": "Download",
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
            3: "Вознаграждение с пополнения реферала", 4: "Конвертация (снятие)",
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
            3: "Реферал толтыру сыйақысы", 4: "Айырбастау (алу)",
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
            3: "Винагорода з поповнення рефералу", 4: "Конвертація (зняття)",
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
            3: "Referral reward", 4: "Conversion (withdrawal)",
            5: "Conversion (credit)", 6: "Chat payment", 7: "Admin top-up",
        },
        "success": "Success!", "fail": "Not completed!",
    },
}


def _process_code_blocks(text: str) -> str:
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


_MIME_OVERRIDES = {
    ".ogg": "audio/ogg", ".oga": "audio/ogg", ".opus": "audio/ogg",
    ".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4",
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp",
    ".pdf": "application/pdf",
}


def _js_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace("\n", "\\n")


def _read_file_b64(file_path: str | None) -> tuple[str, str] | None:
    if not file_path:
        return None
    try:
        p = Path(file_path)
        if not p.exists():
            return None
        data = p.read_bytes()
        b64 = base64.b64encode(data).decode()
        mime = _MIME_OVERRIDES.get(p.suffix.lower()) or mimetypes.guess_type(str(p))[0] or "application/octet-stream"
        return b64, mime
    except Exception:
        return None


def _get_display_name(file_path: str) -> str:
    name = Path(file_path).name
    if name.startswith("doc_") and "_" in name[4:]:
        rest = name[4:]
        idx = rest.find("_")
        if idx != -1:
            return rest[idx + 1:]
    return name


class _MediaContext:
    def __init__(self):
        self.counter = 0
        self.js_entries: list[str] = []

    def render(self, file_type: str | None, file_path: str | None, download_label: str) -> str:
        if not file_type or not file_path:
            return ""
        result = _read_file_b64(file_path)
        if not result:
            return ""
        b64, mime = result
        self.counter += 1
        fid = f"f{self.counter}"
        display_name = _get_display_name(file_path)

        if file_type == "voice":
            return f'<audio controls src="data:{mime};base64,{b64}"></audio>'

        if file_type == "photo":
            img_id = f"img_{fid}"
            return (
                f'<img id="{img_id}" class="media-img" src="data:{mime};base64,{b64}">'
                f'<button class="download-btn" '
                f"onclick=\"downloadFromImg('{img_id}','{_js_escape(display_name)}','{mime}')\">"
                f'📥 {html.escape(download_label)}</button>'
            )

        if file_type == "document":
            self.js_entries.append(f'fileData["{fid}"]="{b64}";')
            return (
                f'<div class="doc-attachment">'
                f'📎 <strong>{html.escape(display_name)}</strong>&nbsp;'
                f'<button class="download-btn" '
                f"onclick=\"downloadFile('{fid}','{_js_escape(display_name)}','{mime}')\">"
                f'📥 {html.escape(download_label)}</button>'
                f'</div>'
            )

        return ""

    def get_file_data_js(self) -> str:
        if not self.js_entries:
            return ""
        return "<script>" + "".join(self.js_entries) + "</script>"


def _build_chat_rows(messages, labels, cur_symbol, ctx: _MediaContext) -> tuple[str, float, int, int]:
    total_cost = 0.0
    total_tokens_in = 0
    total_tokens_out = 0
    rows_html = ""
    i = 0

    while i < len(messages):
        msg = messages[i]
        role_label = labels["user"] if msg["role"] == "user" else labels["ai"]
        content = _process_code_blocks(msg["content"] or "")
        media_html = ctx.render(msg.get("file_type"), msg.get("file_path"), labels["download"])
        if media_html:
            content = media_html + "<br>" + content if content else media_html

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
                ai_media = ctx.render(next_msg.get("file_type"), next_msg.get("file_path"), labels["download"])
                if ai_media:
                    ai_content = ai_media + "<br>" + ai_content if ai_content else ai_media

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

                rows_html += (
                    f'<tr><td>{labels["user"]}</td><td>{content}</td>'
                    f'<td rowspan="2">{spending_html}</td></tr>'
                    f'<tr><td>{labels["ai"]}</td><td>{ai_content}</td></tr>'
                )
                i += 2
                continue

        rows_html += f'<tr><td>{role_label}</td><td>{content}</td><td>{spending_html or "-"}</td></tr>'
        i += 1

    return rows_html, total_cost, total_tokens_in, total_tokens_out


async def export_single_chat(user_id: int, chat_id: int, lang: str = "en") -> str:
    labels = _LABELS.get(lang, _LABELS["en"])
    user = await db.get_user(user_id)
    _, cur_symbol = get_currency(user["country"] if user else None)
    messages = await db.get_chat_messages(user_id, chat_id)

    ctx = _MediaContext()
    rows_html, total_cost, total_tokens_in, total_tokens_out = _build_chat_rows(
        messages, labels, cur_symbol, ctx,
    )

    total_html = labels["total_row"].format(
        tokens_in=total_tokens_in, tokens_out=total_tokens_out,
        tokens_cost=round(total_cost, 4), cur=cur_symbol, total=round(total_cost, 4),
    )

    file_data_js = ctx.get_file_data_js()

    doc = f"""<html>
<head><meta charset="UTF-8"><title>{labels['title']}</title>{_CSS}{_DOWNLOAD_JS}</head>
<body>
<h1>{labels['title']} #{chat_id}</h1>
<table>
<tr><th>{labels['role']}</th><th>{labels['messages']}</th><th>{labels['spending']}</th></tr>
{rows_html}
<tr><td colspan="3">{total_html}</td></tr>
</table>
{file_data_js}
</body></html>"""

    out_dir = _ensure_dir(user_id)
    path = out_dir / f"chat_history{user_id}-{chat_id}.html"
    path.write_text(doc, encoding="utf-8")
    return str(path)


async def export_all_chats(user_id: int, lang: str = "en") -> str:
    labels = _LABELS.get(lang, _LABELS["en"])
    user = await db.get_user(user_id)
    _, cur_symbol = get_currency(user["country"] if user else None)
    chat_ids = await db.get_all_chat_ids(user_id, closed_only=True)

    buttons_html = "   ".join(
        f'<button class="tab-btn" onclick="show_chat({cid})">{labels["chat"]} {cid}</button>'
        for cid in chat_ids
    )

    ctx = _MediaContext()
    chats_html = ""
    for cid in chat_ids:
        messages = await db.get_chat_messages(user_id, cid)
        rows, total_cost, ti, to = _build_chat_rows(messages, labels, cur_symbol, ctx)

        total_html = labels["total_row"].format(
            tokens_in=ti, tokens_out=to,
            tokens_cost=round(total_cost, 4), cur=cur_symbol, total=round(total_cost, 4),
        )
        chats_html += (
            f'<table class="chat" id="chat-{cid}" style="display:none">'
            f'<tr><th>{labels["role"]}</th><th>{labels["messages"]}</th><th>{labels["spending"]}</th></tr>'
            f'{rows}'
            f'<tr><td colspan="3">{total_html}</td></tr>'
            f'</table>'
        )

    file_data_js = ctx.get_file_data_js()

    tab_js = (
        '<script>'
        'function show_chat(id_chat){'
        "var chats=document.getElementsByClassName('chat');"
        'for(var i=0;i<chats.length;i++){chats[i].style.display="none";}'
        "var c=document.getElementById('chat-'+id_chat);"
        'if(c)c.style.display="table";'
        "var cn=document.getElementById('chat-number');"
        'cn.innerHTML=\'<span class="current-chat-label">'
        + labels["current_chat"]
        + " </span>"
        + '<span class="chat-number">\'+id_chat+\'</span>\';'
        '}'
        '</script>'
    )

    doc = f"""<html>
<head><meta charset="UTF-8"><title>{labels['title']}</title>{_CSS}{_DOWNLOAD_JS}{tab_js}</head>
<body>
<h1>{labels['title']}</h1>
{buttons_html}
<div id="chat-number"></div>
{chats_html}
{file_data_js}
</body></html>"""

    out_dir = _ensure_dir(user_id)
    path = out_dir / f"chats_history{user_id}.html"
    path.write_text(doc, encoding="utf-8")
    return str(path)


async def export_transactions(user_id: int, lang: str = "en") -> str:
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
