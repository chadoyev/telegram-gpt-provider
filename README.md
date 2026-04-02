<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/aiogram-3.26-2CA5E0?logo=telegram&logoColor=white" alt="aiogram">
  <img src="https://img.shields.io/badge/OpenAI-GPT--5.4-412991?logo=openai&logoColor=white" alt="OpenAI">
  <img src="https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-green?logo=opensourceinitiative&logoColor=white" alt="MIT License">
</p>

<h1 align="center">UAI Robot</h1>

<p align="center">
  Multilingual Telegram bot powered by OpenAI GPT-5.4 with streaming, voice, vision, image generation, billing & payments
</p>

<p align="center">
  <a href="#-english">English</a> · <a href="#-русский">Русский</a>
</p>

---

<!-- ═══════════════════ ENGLISH ═══════════════════ -->

<a name="-english"></a>

## 🇬🇧 English

### Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start (Docker Compose)](#quick-start-docker-compose)
- [Server Setup & SSL Certificate](#server-setup--ssl-certificate)
- [Payment Systems Configuration](#payment-systems-configuration)
- [Environment Variables](#environment-variables)
- [Running Without Docker](#running-without-docker)
- [Kubernetes Deployment](#kubernetes-deployment)
- [OpenAI Models & Pricing](#openai-models--pricing)
- [License](#license)

---

### Features

- **GPT-5.4 / GPT-5.4 Mini** — text chat with real-time streaming via `send_message_draft` (Bot API 9.5)
- **File Analysis** — PDF, DOCX, PPTX, XLSX, CSV, TXT, code files and more
- **Vision** — photo analysis built into the chat model
- **gpt-4o-transcribe** — voice message transcription (Whisper)
- **gpt-4o-mini-tts** — text-to-speech with 11 voices, emotions, accents
- **gpt-image-1.5** — image generation (both standalone and in-chat via function calling)
- **Billing System** — user balance, top-up, per-request cost tracking
- **Payments** — Robokassa (KZ, UA, Other) + YooKassa (Russia)
- **Referral Program** — sign-up bonuses + percentage reward from referral top-ups
- **Admin Panel** — manage bot settings, broadcast messages, top up user balance
- **Rate Limiting** — DDoS protection with automatic 24h ban for flooding
- **Multilingual** — Russian, Kazakh, Ukrainian, English
- **Multi-currency** — RUB, KZT, UAH, USD with automatic conversion
- **Docker + Kubernetes** — ready-to-deploy configurations with HPA

---

### Tech Stack

| Component   | Technology                                                          |
|-------------|---------------------------------------------------------------------|
| Language    | Python 3.12+                                                        |
| Telegram    | aiogram 3.26 (async, Bot API 9.5, webhook)                         |
| AI          | OpenAI SDK 2.30 — Responses API (streaming, files, vision)         |
| Web Server  | aiohttp (Telegram webhook + payment callbacks)                      |
| Database    | PostgreSQL 16 + asyncpg                                             |
| Payments    | Robokassa, YooKassa                                                 |
| Audio       | FFmpeg (OGG ↔ MP3 conversion)                                      |
| Containers  | Docker + Docker Compose + Kubernetes (HPA autoscaling)              |

---

### Project Structure

```
uai_robot/
├── app/
│   ├── __main__.py          # Entry point: Telegram webhook + aiohttp server
│   ├── config.py            # Configuration from environment variables
│   ├── db.py                # asyncpg: connection pool, queries, schema
│   ├── billing.py           # Billing, currencies, cost calculation
│   ├── openai_client.py     # OpenAI Responses API: streaming, files, vision, TTS, STT
│   ├── keyboards.py         # Inline keyboards
│   ├── middlewares.py        # Middleware: user registration, bot status, rate limiter
│   ├── webhooks.py          # aiohttp: payment webhooks + /health
│   ├── chat_export.py       # HTML export of chat history & transactions
│   ├── utils.py             # Utilities: FFmpeg, base64, directories
│   ├── handlers/
│   │   ├── start.py         # /start, language, country, terms of use
│   │   ├── chat.py          # Chat: text, voice, photo, documents + streaming
│   │   ├── menu.py          # Account, settings, chat history
│   │   ├── admin.py         # Admin panel
│   │   ├── payments.py      # Payments, transactions
│   │   └── image_gen.py     # Standalone image generation
│   └── locales/
│       └── loader.py        # i18n: RU/KZ/UA/EN
├── k8s/                     # Kubernetes manifests
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── schema.sql               # Reference SQL schema
├── requirements.txt
├── LICENSE
└── README.md
```

---

### Prerequisites

- **VPS / Dedicated Server** with a public IP address
- **Domain name** pointed to your server (required for HTTPS webhook & payment callbacks)
- **SSL certificate** (Let's Encrypt is free and works great)
- **Docker** and **Docker Compose** installed on the server
- **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
- **OpenAI API Key** from [platform.openai.com](https://platform.openai.com/)
- **FFmpeg** (included in Docker image, only needed for non-Docker installs)

---

### Quick Start (Docker Compose)

#### 1. Clone the repository

```bash
git clone https://github.com/chadoyev/telegram-gpt-provider.git
cd telegram-gpt-provider
```

#### 2. Configure environment

```bash
cp .env.example .env
nano .env   # fill in your values
```

Fill in at minimum:

| Variable           | Description                                              |
|--------------------|----------------------------------------------------------|
| `API_TOKEN`        | Telegram bot token from @BotFather                       |
| `ADMIN_ID`         | Your Telegram user ID (get it from @userinfobot)         |
| `OPENAI_API_KEY`   | OpenAI API key                                           |
| `DB_PASSWORD`      | PostgreSQL password (you choose)                         |
| `WEBHOOK_BASE_URL` | Public HTTPS URL, e.g. `https://bot.yourdomain.com`     |
| `WEBHOOK_SECRET`   | Random string for webhook verification                   |

#### 3. Build and start

```bash
docker compose up -d --build
```

The bot and PostgreSQL will start. Database tables are created automatically on first launch.

#### 4. Verify

```bash
docker compose logs -f bot
```

You should see:
```
Database initialized
Telegram webhook set: https://bot.yourdomain.com/tg
Webhook server started on 0.0.0.0:8443
```

---

### Server Setup & SSL Certificate

The bot uses webhooks, which require HTTPS. Payment systems (Robokassa, YooKassa) also require a valid domain with SSL. Here is a complete setup guide.

#### 1. Install Docker on your server

```bash
# Ubuntu / Debian
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

#### 2. Point your domain to the server

Add an **A record** in your DNS provider pointing your domain (e.g. `bot.yourdomain.com`) to your server's IP address.

#### 3. Obtain SSL certificate with Certbot

```bash
sudo apt install -y certbot
sudo certbot certonly --standalone -d bot.yourdomain.com
```

Certificates will be saved at:
- `/etc/letsencrypt/live/bot.yourdomain.com/fullchain.pem`
- `/etc/letsencrypt/live/bot.yourdomain.com/privkey.pem`

Set up auto-renewal:

```bash
sudo certbot renew --dry-run
```

#### 4. Set up Nginx as reverse proxy

```bash
sudo apt install -y nginx
```

Create `/etc/nginx/sites-available/uai-robot`:

```nginx
server {
    listen 443 ssl;
    server_name bot.yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/bot.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bot.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name bot.yourdomain.com;
    return 301 https://$host$request_uri;
}
```

Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/uai-robot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. Set WEBHOOK_BASE_URL in `.env`

```
WEBHOOK_BASE_URL=https://bot.yourdomain.com
```

> **Important:** The URL must be HTTPS. The bot listens on port 8443, Nginx proxies 443 → 8443.

---

### Payment Systems Configuration

Both payment systems send callbacks to your server over HTTPS, which is why a domain + SSL is required.

#### Test mode vs production (`TEST_MODE_PAY_SYSTEM`)

Set in `.env`:

| Value | Effect |
|-------|--------|
| `true` | **Test mode:** Robokassa uses `IsTest=1`; YooKassa creates payments with `test: true`. Use **test** shop credentials (test login/passwords from each provider’s dashboard). |
| `false` or unset (default) | **Production:** Robokassa `IsTest=0`; YooKassa real payments. Use **live** credentials only. |

The same variable names (`ROBOKASSA_*`, `YOOKASSA_*`) always hold the credentials for the mode you are in—switch the flag **and** replace the secrets when moving from sandbox to production.

#### Robokassa (KZ, UA, Other countries)

1. Register at [robokassa.com](https://robokassa.com) and create a store
2. In the store settings, set **Result URL** to: `https://bot.yourdomain.com/robokassa` (GET method)
3. Fill in `.env`:
   ```
   ROBOKASSA_LOGIN=your_login
   ROBOKASSA_PASS1=your_password_1
   ROBOKASSA_PASS2=your_password_2
   ```

#### YooKassa (Russia)

1. Register at [yookassa.ru](https://yookassa.ru) and create a store
2. In the store settings, set **HTTP notification URL** to: `https://bot.yourdomain.com/yookassa` (POST method)
3. Enable the event: `payment.succeeded`
4. Fill in `.env`:
   ```
   YOOKASSA_ACCOUNT_ID=your_shop_id
   YOOKASSA_SECRET_KEY=your_secret_key
   RECEIPT_EMAIL=receipt@yourdomain.com
   RECEIPT_PHONE=+79999999999
   ```

---

### Environment Variables

| Variable               | Required | Default          | Description                                                |
|------------------------|----------|------------------|------------------------------------------------------------|
| `API_TOKEN`            | Yes      | —                | Telegram Bot Token                                         |
| `ADMIN_ID`             | Yes      | `0`              | Telegram ID of the administrator                           |
| `PASSWORD_ADMIN`       | No       | `Admin`          | Password to open admin panel (send as message)             |
| `OPENAI_API_KEY`       | Yes      | —                | OpenAI API key                                             |
| `DB_HOST`              | No       | `postgres`       | PostgreSQL host                                            |
| `DB_PORT`              | No       | `5432`           | PostgreSQL port                                            |
| `DB_USER`              | No       | `postgres`       | PostgreSQL user                                            |
| `DB_PASSWORD`          | Yes      | —                | PostgreSQL password                                        |
| `DB_NAME`              | No       | `uai_robot`      | PostgreSQL database name                                   |
| `TEST_MODE_PAY_SYSTEM` | No       | `false`          | Payment sandbox: `true` = test (`IsTest` / YooKassa `test`); use test credentials in `ROBOKASSA_*` / `YOOKASSA_*` |
| `ROBOKASSA_LOGIN`      | No       | —                | Robokassa merchant login                                   |
| `ROBOKASSA_PASS1`      | No       | —                | Robokassa password #1                                      |
| `ROBOKASSA_PASS2`      | No       | —                | Robokassa password #2                                      |
| `YOOKASSA_ACCOUNT_ID`  | No       | —                | YooKassa shop ID                                           |
| `YOOKASSA_SECRET_KEY`  | No       | —                | YooKassa secret key                                        |
| `RECEIPT_EMAIL`        | No       | `receipt@example.com` | Email for YooKassa receipts                           |
| `RECEIPT_PHONE`        | No       | `+79999999999`   | Phone for YooKassa receipts                                |
| `URL_SUPPORT`          | No       | —                | Support Telegram link (shown in account menu)              |
| `URL_BOT`              | No       | —                | Bot link `https://t.me/your_bot` (used for referral links) |
| `URL_CHANNEL`          | No       | —                | Channel link                                               |
| `WEBHOOK_HOST`         | No       | `0.0.0.0`        | Webhook server bind host                                   |
| `WEBHOOK_PORT`         | No       | `8443`           | Webhook server port                                        |
| `WEBHOOK_BASE_URL`     | Yes      | —                | Public HTTPS URL (e.g. `https://bot.yourdomain.com`)       |
| `WEBHOOK_SECRET`       | No       | —                | Secret token for Telegram webhook verification             |
| `MESSAGES_DIR`         | No       | `users`          | Directory for user files (voice, photos, exports)          |

---

### Running Without Docker

#### Requirements

- Python 3.12+
- PostgreSQL 16+
- FFmpeg installed and in PATH

#### Installation

```bash
git clone https://github.com/chadoyev/telegram-gpt-provider.git
cd telegram-gpt-provider

python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

#### Create the database

```bash
createdb uai_robot
# or: psql -U postgres -c "CREATE DATABASE uai_robot;"
```

#### Configure and run

```bash
cp .env.example .env
# Edit .env — set DB_HOST=127.0.0.1 for local PostgreSQL

python -m app
```

---

### Kubernetes Deployment

#### 1. Build and push the Docker image

```bash
docker build -t chadoyev/uai-robot:latest .
docker push chadoyev/uai-robot:latest
```

#### 2. Edit secrets

Edit `k8s/secrets.yaml` — replace all `CHANGE_ME` with your real values.

#### 3. Apply manifests

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/bot-deployment.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml   # if you need Ingress for webhooks
```

#### 4. Verify

```bash
kubectl -n uai-robot get pods
kubectl -n uai-robot logs -f deployment/uai-robot-bot
```

HPA is configured for 1–10 replicas scaling on CPU (70%) and memory (80%).

---

### OpenAI Models & Pricing

| Model             | Description                           | API Price                               |
|-------------------|---------------------------------------|-----------------------------------------|
| GPT-5.4 Mini      | Fast model for everyday tasks        | $0.75 / $4.50 per 1M tokens (in/out)   |
| GPT-5.4            | Flagship model                       | $2.50 / $15.00 per 1M tokens (in/out)  |
| gpt-4o-transcribe  | Speech recognition (Whisper)         | $0.006 / minute                         |
| gpt-4o-mini-tts    | Text-to-speech (11 voices)           | $18 / 1M characters                     |
| gpt-image-1.5      | Image generation                     | $0.034 / image (1024×1024)              |

#### Supported File Formats

- **Images:** JPG, PNG, GIF, WebP
- **Documents:** PDF, DOC, DOCX, PPT, PPTX
- **Spreadsheets:** CSV, TSV, XLS, XLSX
- **Text / Code:** TXT, MD, JSON, XML, YAML, PY, JS, TS, HTML, CSS

---

### License

MIT — see [LICENSE](LICENSE).

---

<!-- ═══════════════════ РУССКИЙ ═══════════════════ -->

<a name="-русский"></a>

## 🇷🇺 Русский

### Содержание

- [Возможности](#возможности)
- [Технологии](#технологии)
- [Структура проекта](#структура-проекта)
- [Что потребуется](#что-потребуется)
- [Быстрый старт (Docker Compose)](#быстрый-старт-docker-compose)
- [Настройка сервера и SSL-сертификата](#настройка-сервера-и-ssl-сертификата)
- [Настройка платёжных систем](#настройка-платёжных-систем)
- [Переменные окружения](#переменные-окружения)
- [Запуск без Docker](#запуск-без-docker)
- [Деплой в Kubernetes](#деплой-в-kubernetes)
- [Модели OpenAI и цены](#модели-openai-и-цены)
- [Лицензия](#лицензия)

---

### Возможности

- **GPT-5.4 / GPT-5.4 Mini** — текстовый чат с потоковой передачей ответа через `send_message_draft` (Bot API 9.5)
- **Анализ файлов** — PDF, DOCX, PPTX, XLSX, CSV, TXT, код и другие форматы
- **Vision** — анализ фотографий, встроенный в модель
- **gpt-4o-transcribe** — распознавание голосовых сообщений (Whisper)
- **gpt-4o-mini-tts** — озвучивание ответов: 11 голосов, эмоции, акценты
- **gpt-image-1.5** — генерация изображений (отдельно и в чате через function calling)
- **Биллинг** — баланс пользователя, пополнение, учёт расходов за каждый запрос
- **Платежи** — Robokassa (KZ, UA, Other) + YooKassa (Россия)
- **Реферальная программа** — бонусы за регистрацию + процент с пополнений рефералов
- **Админ-панель** — управление настройками бота, рассылка, пополнение баланса пользователей
- **Rate Limiting** — защита от DDoS с автоматическим баном на 24 часа
- **Мультиязычность** — русский, казахский, украинский, английский
- **Мультивалютность** — RUB, KZT, UAH, USD с автоматической конвертацией
- **Docker + Kubernetes** — готовые конфигурации с HPA автоскейлингом

---

### Технологии

| Компонент      | Технология                                                         |
|----------------|--------------------------------------------------------------------|
| Язык           | Python 3.12+                                                       |
| Telegram       | aiogram 3.26 (async, Bot API 9.5, webhook)                        |
| ИИ             | OpenAI SDK 2.30 — Responses API (стриминг, файлы, vision)         |
| Веб-сервер     | aiohttp (Telegram webhook + коллбэки платёжных систем)             |
| База данных    | PostgreSQL 16 + asyncpg                                            |
| Платежи        | Robokassa, YooKassa                                                |
| Аудио          | FFmpeg (конвертация OGG ↔ MP3)                                     |
| Контейнеры     | Docker + Docker Compose + Kubernetes (HPA)                         |

---

### Структура проекта

```
uai_robot/
├── app/
│   ├── __main__.py          # Точка входа: Telegram webhook + aiohttp сервер
│   ├── config.py            # Конфигурация из переменных окружения
│   ├── db.py                # asyncpg: пул подключений, запросы, схема
│   ├── billing.py           # Биллинг, валюты, расчёт стоимости
│   ├── openai_client.py     # OpenAI Responses API: стриминг, файлы, vision, TTS, STT
│   ├── keyboards.py         # Inline-клавиатуры
│   ├── middlewares.py       # Middleware: регистрация, статус бота, rate limiter
│   ├── webhooks.py          # aiohttp: вебхуки платежей + /health
│   ├── chat_export.py       # HTML-экспорт истории чатов и транзакций
│   ├── utils.py             # Утилиты: FFmpeg, base64, директории
│   ├── handlers/
│   │   ├── start.py         # /start, язык, страна, соглашение
│   │   ├── chat.py          # Чат: текст, голос, фото, документы + стриминг
│   │   ├── menu.py          # Аккаунт, настройки, история чатов
│   │   ├── admin.py         # Админ-панель
│   │   ├── payments.py      # Оплата, транзакции
│   │   └── image_gen.py     # Генерация изображений
│   └── locales/
│       └── loader.py        # i18n: RU/KZ/UA/EN
├── k8s/                     # Kubernetes манифесты
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── schema.sql               # SQL-схема для справки
├── requirements.txt
├── LICENSE
└── README.md
```

---

### Что потребуется

- **VPS / Выделенный сервер** с публичным IP-адресом
- **Доменное имя**, направленное на сервер (необходимо для HTTPS-вебхуков и коллбэков платёжек)
- **SSL-сертификат** (Let's Encrypt — бесплатный и отлично работает)
- **Docker** и **Docker Compose** установлены на сервере
- **Telegram Bot Token** от [@BotFather](https://t.me/BotFather)
- **OpenAI API Key** с [platform.openai.com](https://platform.openai.com/)
- **FFmpeg** (уже включён в Docker-образ, нужен только для запуска без Docker)

---

### Быстрый старт (Docker Compose)

#### 1. Клонировать репозиторий

```bash
git clone https://github.com/chadoyev/telegram-gpt-provider.git
cd telegram-gpt-provider
```

#### 2. Настроить переменные окружения

```bash
cp .env.example .env
nano .env   # заполнить своими значениями
```

Обязательно заполнить:

| Переменная          | Описание                                                    |
|---------------------|-------------------------------------------------------------|
| `API_TOKEN`         | Токен бота от @BotFather                                    |
| `ADMIN_ID`          | Ваш Telegram ID (узнать у @userinfobot)                     |
| `OPENAI_API_KEY`    | API-ключ OpenAI                                             |
| `DB_PASSWORD`       | Пароль PostgreSQL (выбираете сами)                          |
| `WEBHOOK_BASE_URL`  | Публичный HTTPS URL, напр. `https://bot.yourdomain.com`    |
| `WEBHOOK_SECRET`    | Случайная строка для верификации webhook                    |

#### 3. Собрать и запустить

```bash
docker compose up -d --build
```

Бот и PostgreSQL запустятся. Таблицы в БД создаются автоматически при первом запуске.

#### 4. Проверить

```bash
docker compose logs -f bot
```

Должны увидеть:
```
Database initialized
Telegram webhook set: https://bot.yourdomain.com/tg
Webhook server started on 0.0.0.0:8443
```

---

### Настройка сервера и SSL-сертификата

Бот работает через webhooks, для которых обязателен HTTPS. Платёжные системы (Robokassa, YooKassa) также требуют домен с SSL-сертификатом. Ниже полная инструкция по настройке.

#### 1. Установить Docker на сервер

```bash
# Ubuntu / Debian
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

#### 2. Направить домен на сервер

Добавьте **A-запись** у вашего DNS-провайдера, указав домен (напр. `bot.yourdomain.com`) на IP-адрес вашего сервера.

#### 3. Получить SSL-сертификат через Certbot

```bash
sudo apt install -y certbot
sudo certbot certonly --standalone -d bot.yourdomain.com
```

Сертификаты будут сохранены в:
- `/etc/letsencrypt/live/bot.yourdomain.com/fullchain.pem`
- `/etc/letsencrypt/live/bot.yourdomain.com/privkey.pem`

Настройте автопродление:

```bash
sudo certbot renew --dry-run
```

#### 4. Настроить Nginx как обратный прокси

```bash
sudo apt install -y nginx
```

Создайте файл `/etc/nginx/sites-available/uai-robot`:

```nginx
server {
    listen 443 ssl;
    server_name bot.yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/bot.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bot.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name bot.yourdomain.com;
    return 301 https://$host$request_uri;
}
```

Активировать сайт и перезапустить Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/uai-robot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. Указать WEBHOOK_BASE_URL в `.env`

```
WEBHOOK_BASE_URL=https://bot.yourdomain.com
```

> **Важно:** URL должен быть HTTPS. Бот слушает порт 8443, Nginx проксирует 443 → 8443.

---

### Настройка платёжных систем

Обе платёжные системы отправляют коллбэки на ваш сервер по HTTPS, поэтому домен с SSL-сертификатом обязателен.

#### Тестовый режим и прод (`TEST_MODE_PAY_SYSTEM`)

В `.env`:

| Значение | Поведение |
|----------|-----------|
| `true` | **Тест:** у Robokassa `IsTest=1`, у YooKassa платежи с `test: true`. В `ROBOKASSA_*` и `YOOKASSA_*` указывайте **тестовые** данные магазина из личных кабинетов. |
| `false` или не задано (по умолчанию) | **Прод:** Robokassa `IsTest=0`, YooKassa — реальные платежи. Только **боевые** ключи и пароли. |

Имена переменных те же; при переходе из песочницы в прод поменяйте флаг **и** замените секреты на продовые.

#### Robokassa (Казахстан, Украина, другие страны)

1. Зарегистрируйтесь на [robokassa.com](https://robokassa.com) и создайте магазин
2. В настройках магазина укажите **Result URL**: `https://bot.yourdomain.com/robokassa` (метод GET)
3. Заполните в `.env`:
   ```
   ROBOKASSA_LOGIN=ваш_логин
   ROBOKASSA_PASS1=ваш_пароль_1
   ROBOKASSA_PASS2=ваш_пароль_2
   ```

#### YooKassa (Россия)

1. Зарегистрируйтесь на [yookassa.ru](https://yookassa.ru) и создайте магазин
2. В настройках магазина укажите **URL для HTTP-уведомлений**: `https://bot.yourdomain.com/yookassa` (метод POST)
3. Включите событие: `payment.succeeded`
4. Заполните в `.env`:
   ```
   YOOKASSA_ACCOUNT_ID=ваш_shop_id
   YOOKASSA_SECRET_KEY=ваш_секретный_ключ
   RECEIPT_EMAIL=receipt@yourdomain.com
   RECEIPT_PHONE=+79999999999
   ```

---

### Переменные окружения

| Переменная              | Обязат. | По умолчанию          | Описание                                                   |
|-------------------------|---------|------------------------|-------------------------------------------------------------|
| `API_TOKEN`             | Да      | —                      | Токен Telegram-бота                                         |
| `ADMIN_ID`              | Да      | `0`                    | Telegram ID администратора                                  |
| `PASSWORD_ADMIN`        | Нет     | `Admin`                | Пароль для админ-панели (отправляется сообщением)           |
| `OPENAI_API_KEY`        | Да      | —                      | API-ключ OpenAI                                             |
| `DB_HOST`               | Нет     | `postgres`             | Хост PostgreSQL                                             |
| `DB_PORT`               | Нет     | `5432`                 | Порт PostgreSQL                                             |
| `DB_USER`               | Нет     | `postgres`             | Пользователь PostgreSQL                                     |
| `DB_PASSWORD`           | Да      | —                      | Пароль PostgreSQL                                           |
| `DB_NAME`               | Нет     | `uai_robot`            | Имя базы данных                                             |
| `TEST_MODE_PAY_SYSTEM`  | Нет     | `false`                | Тест платежей: `true` — тестовый режим; в `ROBOKASSA_*` / `YOOKASSA_*` — тестовые кабинеты |
| `ROBOKASSA_LOGIN`       | Нет     | —                      | Логин Robokassa                                             |
| `ROBOKASSA_PASS1`       | Нет     | —                      | Пароль №1 Robokassa                                         |
| `ROBOKASSA_PASS2`       | Нет     | —                      | Пароль №2 Robokassa                                         |
| `YOOKASSA_ACCOUNT_ID`   | Нет     | —                      | Shop ID YooKassa                                            |
| `YOOKASSA_SECRET_KEY`   | Нет     | —                      | Секретный ключ YooKassa                                     |
| `RECEIPT_EMAIL`         | Нет     | `receipt@example.com`  | Email для чеков YooKassa                                    |
| `RECEIPT_PHONE`         | Нет     | `+79999999999`         | Телефон для чеков YooKassa                                  |
| `URL_SUPPORT`           | Нет     | —                      | Ссылка на поддержку в Telegram                              |
| `URL_BOT`               | Нет     | —                      | Ссылка на бота `https://t.me/your_bot` (для рефералов)     |
| `URL_CHANNEL`           | Нет     | —                      | Ссылка на канал                                             |
| `WEBHOOK_HOST`          | Нет     | `0.0.0.0`             | Хост webhook-сервера                                        |
| `WEBHOOK_PORT`          | Нет     | `8443`                 | Порт webhook-сервера                                        |
| `WEBHOOK_BASE_URL`      | Да      | —                      | Публичный HTTPS URL (напр. `https://bot.yourdomain.com`)   |
| `WEBHOOK_SECRET`        | Нет     | —                      | Секрет для верификации Telegram webhook                     |
| `MESSAGES_DIR`          | Нет     | `users`                | Директория для файлов пользователей                         |

---

### Запуск без Docker

#### Требования

- Python 3.12+
- PostgreSQL 16+
- FFmpeg установлен и доступен в PATH

#### Установка

```bash
git clone https://github.com/chadoyev/telegram-gpt-provider.git
cd telegram-gpt-provider

python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

#### Создать базу данных

```bash
createdb uai_robot
# или: psql -U postgres -c "CREATE DATABASE uai_robot;"
```

#### Настроить и запустить

```bash
cp .env.example .env
# Отредактируйте .env — укажите DB_HOST=127.0.0.1 для локального PostgreSQL

python -m app
```

---

### Деплой в Kubernetes

#### 1. Собрать и запушить Docker-образ

```bash
docker build -t chadoyev/uai-robot:latest .
docker push chadoyev/uai-robot:latest
```

#### 2. Отредактировать секреты

Отредактируйте `k8s/secrets.yaml` — замените все `CHANGE_ME` на реальные значения.

#### 3. Применить манифесты

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/bot-deployment.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml   # если нужен Ingress для вебхуков
```

#### 4. Проверить

```bash
kubectl -n uai-robot get pods
kubectl -n uai-robot logs -f deployment/uai-robot-bot
```

HPA настроен на 1–10 реплик с масштабированием по CPU (70%) и памяти (80%).

---

### Модели OpenAI и цены

| Модель              | Описание                              | Цена API                                |
|---------------------|---------------------------------------|-----------------------------------------|
| GPT-5.4 Mini        | Быстрая модель для повседневных задач | $0.75 / $4.50 за 1M токенов (вход/вых) |
| GPT-5.4             | Флагманская модель                    | $2.50 / $15.00 за 1M токенов (вход/вых)|
| gpt-4o-transcribe   | Распознавание речи (Whisper)          | $0.006 / минута                         |
| gpt-4o-mini-tts     | Озвучивание текста (11 голосов)        | $18 / 1M символов                       |
| gpt-image-1.5       | Генерация изображений                 | $0.034 / изображение (1024×1024)        |

#### Поддерживаемые форматы файлов

- **Изображения:** JPG, PNG, GIF, WebP
- **Документы:** PDF, DOC, DOCX, PPT, PPTX
- **Таблицы:** CSV, TSV, XLS, XLSX
- **Текст / Код:** TXT, MD, JSON, XML, YAML, PY, JS, TS, HTML, CSS

---

### Лицензия

MIT — см. файл [LICENSE](LICENSE).
