from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.config import settings, VOICES
from app.locales import t


def _btn(text: str, callback_data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback_data)


def _url_btn(text: str, url: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, url=url)


# ── Language / Country ──────────────────────────────────────────

def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("Русский язык", "lang:ru")],
        [_btn("Қазақ тілі", "lang:kz")],
        [_btn("Українська мова", "lang:ua")],
        [_btn("English", "lang:en")],
    ])


def country_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("🇷🇺 Россия ₽", "country:Россия")],
        [_btn("🇰🇿 Қазақстан ₸", "country:Казахстан")],
        [_btn("🇺🇦 Україна ₴", "country:Украина")],
        [_btn("🌍 Other $", "country:Other")],
    ])


def terms_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(f"✅ {t('btn_accept', lang)}", "accept_terms")],
    ])


# ── Welcome / Main ─────────────────────────────────────────────

def welcome_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(f"👤 {t('btn_account', lang)}", "account")],
        [_btn(f"🟢 {t('btn_start_chat', lang)}", "start_chat")],
        [_btn(f"🖼 {t('btn_generate_image', lang)}", "gen_image")],
    ])


# ── Chat ────────────────────────────────────────────────────────

def chat_keyboard(lang: str, voice_on: bool = False) -> InlineKeyboardMarkup:
    voice_text = t("btn_voice_off", lang) if voice_on else t("btn_voice_on", lang)
    voice_cb = "voice_off" if voice_on else "voice_on"
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(f"🔊 {voice_text}", voice_cb)],
        [_btn(f"🔴 {t('btn_end_chat', lang)}", "end_chat")],
    ])


# ── Account Menu ────────────────────────────────────────────────

def account_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [_btn(f"💳 {t('btn_top_up', lang)}", "top_up")],
        [_btn(f"🤖 {t('btn_change_model', lang)}", "change_model")],
        [_btn(f"🔊 {t('btn_change_voice', lang)}", "change_voice")],
        [_btn(f"🧾 {t('btn_transactions', lang)}", "my_transactions")],
        [_btn(f"💬 {t('btn_my_chats', lang)}", "chats_menu")],
        [_btn(f"🌐 {t('btn_change_country', lang)}", "change_country")],
        [_btn(f"🗣 {t('btn_change_lang', lang)}", "change_lang")],
        [_btn(f"ℹ️ {t('btn_prices', lang)}", "prices")],
        [_url_btn(f"🆘 {t('btn_support', lang)}", settings.telegram.support_url)],
        [_btn(f"↩ {t('btn_back', lang)}", "welcome")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def chats_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(f"💬 {t('btn_get_all_chats', lang)}", "get_all_chats")],
        [_btn(f"🗨 {t('btn_get_chat', lang)}", "get_one_chat")],
        [_btn(f"🗑 {t('btn_delete_history', lang)}", "delete_history")],
        [_btn(f"↩ {t('btn_back', lang)}", "account")],
    ])


# ── Model ───────────────────────────────────────────────────────

def model_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("🧠 GPT-5.4", "model:gpt-5.4")],
        [_btn("🚀 GPT-5.4 Mini", "model:gpt-5.4-mini")],
        [_btn(f"↩ {t('btn_back', lang)}", "account")],
    ])


# ── Voice ───────────────────────────────────────────────────────

def voice_keyboard(lang: str) -> InlineKeyboardMarkup:
    voices = VOICES.get(lang, VOICES["en"])
    rows = [[_btn(f"🎙 {name}", f"set_voice:{key}")] for key, name in voices.items()]
    rows.append([_btn(f"↩ {t('btn_back', lang)}", "account")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── Payments ────────────────────────────────────────────────────

def payment_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("5$", "pay:5"), _btn("10$", "pay:10"), _btn("25$", "pay:25")],
        [_btn("50$", "pay:50"), _btn("100$", "pay:100")],
        [_btn(f"↩ {t('btn_back', lang)}", "account")],
    ])


# ── Utility ─────────────────────────────────────────────────────

def close_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(f"❌ {t('btn_close', lang)}", "close_msg")],
    ])


def back_keyboard(lang: str, target: str = "account") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn(f"↩ {t('btn_back', lang)}", target)],
    ])
