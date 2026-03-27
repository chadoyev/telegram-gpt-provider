from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _env(key: str, default: str | None = None, *, required: bool = False) -> str:
    val = os.getenv(key, default)
    if required and not val:
        raise RuntimeError(f"Missing required env var: {key}")
    return val or ""


@dataclass(frozen=True)
class TelegramConfig:
    token: str = field(default_factory=lambda: _env("API_TOKEN", required=True))
    admin_id: int = field(default_factory=lambda: int(_env("ADMIN_ID", "0")))
    admin_password: str = field(default_factory=lambda: _env("PASSWORD_ADMIN", "Admin"))
    channel_username: str = field(default_factory=lambda: _env("URL_CHANNEL", ""))
    bot_url: str = field(default_factory=lambda: _env("URL_BOT", ""))
    support_url: str = field(default_factory=lambda: _env("URL_SUPPORT", ""))


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str = field(default_factory=lambda: _env("OPENAI_API_KEY", required=True))
    base_url: str = field(default_factory=lambda: _env("OPENAI_API_BASE", "https://api.openai.com/v1"))
    default_model: str = "gpt-5.4-mini"
    premium_model: str = "gpt-5.4"
    image_model: str = "gpt-image-1.5"
    tts_model: str = "gpt-4o-mini-tts"
    stt_model: str = "gpt-4o-mini-transcribe"
    max_tokens: int = 4096


@dataclass(frozen=True)
class DatabaseConfig:
    host: str = field(default_factory=lambda: _env("DB_HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: int(_env("DB_PORT", "5432")))
    user: str = field(default_factory=lambda: _env("DB_USER", "postgres"))
    password: str = field(default_factory=lambda: _env("DB_PASSWORD", ""))
    name: str = field(default_factory=lambda: _env("DB_NAME", "uai_robot"))
    min_pool: int = 2
    max_pool: int = 20

    @property
    def dsn(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass(frozen=True)
class FreeKassaConfig:
    secret1: str = field(default_factory=lambda: _env("FREEKASSA_SECRET1", ""))
    secret2: str = field(default_factory=lambda: _env("FREEKASSA_SECRET2", ""))
    merchant_id: str = field(default_factory=lambda: _env("FREEKASSA_MERCHANT_ID", ""))
    server_ip: str = field(default_factory=lambda: _env("FREEKASSA_IP_SERVER", ""))


@dataclass(frozen=True)
class RobokassaConfig:
    login: str = field(default_factory=lambda: _env("ROBOKASSA_LOGIN", ""))
    pass1: str = field(default_factory=lambda: _env("ROBOKASSA_PASS1", ""))
    pass2: str = field(default_factory=lambda: _env("ROBOKASSA_PASS2", ""))


@dataclass(frozen=True)
class YooKassaConfig:
    account_id: str = field(default_factory=lambda: _env("YOOKASSA_ACCOUNT_ID", ""))
    secret_key: str = field(default_factory=lambda: _env("YOOKASSA_SECRET_KEY", ""))
    receipt_email: str = field(default_factory=lambda: _env("RECEIPT_EMAIL", ""))


@dataclass(frozen=True)
class Settings:
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    freekassa: FreeKassaConfig = field(default_factory=FreeKassaConfig)
    robokassa: RobokassaConfig = field(default_factory=RobokassaConfig)
    yookassa: YooKassaConfig = field(default_factory=YooKassaConfig)
    messages_dir: str = field(default_factory=lambda: _env("MESSAGES_DIR", "users"))
    webhook_port: int = field(default_factory=lambda: int(_env("WEBHOOK_PORT", "8443")))
    webhook_host: str = field(default_factory=lambda: _env("WEBHOOK_HOST", "0.0.0.0"))
    ssl_cert: str = field(default_factory=lambda: _env("SSL_CERT", ""))
    ssl_key: str = field(default_factory=lambda: _env("SSL_KEY", ""))


settings = Settings()

SYSTEM_PROMPT = (
    "You are a paid helpful assistant in a Telegram bot. "
    "You communicate with a user. The maximum length of one answer is 4000 characters. "
    "Consider the maximum length when creating large responses. "
    "You can answer by text, generate voice responses, understand photos and documents, "
    "and generate images via DALL-E. "
    "Your services are paid because you work through the official OpenAI API."
)

VOICES = {
    "ru": {
        "alloy": "Алиса", "ash": "Артём", "ballad": "Борис",
        "coral": "Карина", "echo": "Андрей", "fable": "Дмитрий",
        "nova": "Вероника", "onyx": "Тимофей", "sage": "Софья",
        "shimmer": "Анастасия", "verse": "Виктор",
    },
    "kz": {
        "alloy": "Адель", "ash": "Арман", "ballad": "Бауыржан",
        "coral": "Камила", "echo": "Айдар", "fable": "Дамир",
        "nova": "Асель", "onyx": "Тамерлан", "sage": "Сара",
        "shimmer": "Әлия", "verse": "Олжас",
    },
    "ua": {
        "alloy": "Аліса", "ash": "Артем", "ballad": "Богдан",
        "coral": "Каріна", "echo": "Андрій", "fable": "Дмитро",
        "nova": "Вероніка", "onyx": "Тимофій", "sage": "Софія",
        "shimmer": "Анастасія", "verse": "Віктор",
    },
    "en": {
        "alloy": "Alloy", "ash": "Ash", "ballad": "Ballad",
        "coral": "Coral", "echo": "Echo", "fable": "Fable",
        "nova": "Nova", "onyx": "Onyx", "sage": "Sage",
        "shimmer": "Shimmer", "verse": "Verse",
    },
}
