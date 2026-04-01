# UAI Robot — Telegram-бот с доступом к OpenAI GPT-5.4

Асинхронный Telegram-бот на **aiogram 3.26** + **OpenAI Responses API**, который предоставляет пользователям платный доступ к GPT-5.4. Поддерживает **стриминг ответов**, **текст**, **голос (gpt-4o-transcribe + gpt-4o-mini-tts)**, **анализ изображений**, **анализ документов (PDF, DOCX, XLSX, TXT)**, **генерацию картинок (gpt-image-1.5)**, **многоязычный интерфейс (RU/KZ/UA/EN)** и встроенную **платёжную систему**.

---

## Возможности

- **GPT-5.4 / GPT-5.4 Mini** — текстовый чат с потоковой передачей ответа (streaming)
- **Файлы** — анализ PDF, DOCX, PPTX, XLSX, CSV, TXT, код и другие форматы
- **Vision** — анализ фотографий, встроенный в модель
- **gpt-4o-transcribe** — распознавание голосовых сообщений
- **gpt-4o-mini-tts** — озвучивание ответов (11 голосов, эмоции, акценты)
- **gpt-image-1.5** — генерация изображений (замена DALL-E 3)
- **Стриминг** — ответы нейросети показываются в реальном времени через `send_message_draft` (Bot API 9.5)
- **Биллинг** — баланс, пополнение, транзакции
- **Платежи** — Robokassa, YooKassa
- **Рефералка** — бонусы за приведённых пользователей
- **Админ-панель** — управление ботом из Telegram
- **Docker + Kubernetes** — готовые конфигурации для деплоя

---

## Технологии

| Компонент     | Стек                                              |
| ------------- | ------------------------------------------------- |
| Язык          | Python 3.12+                                      |
| Telegram      | aiogram 3.26 (async, Bot API 9.5)                 |
| OpenAI        | openai 2.30 — Responses API (streaming, файлы, vision) |
| Web           | aiohttp (Telegram webhook + платёжные коллбэки)   |
| База данных   | PostgreSQL 16 + asyncpg                           |
| Платежи       | Robokassa, YooKassa                               |
| Аудио         | FFmpeg (OGG ↔ MP3)                                |
| Контейнеры    | Docker + Docker Compose + Kubernetes (HPA)        |

---

## Структура проекта

```
uai_robot/
├── app/
│   ├── __init__.py
│   ├── __main__.py          # точка входа: Telegram webhook + aiohttp
│   ├── config.py             # конфигурация из env
│   ├── db.py                 # asyncpg: подключение, запросы
│   ├── billing.py            # биллинг, валюты, списание
│   ├── openai_client.py      # OpenAI Responses API: стриминг, файлы, vision, TTS, STT
│   ├── keyboards.py          # inline-клавиатуры
│   ├── middlewares.py         # middleware: регистрация, статус бота
│   ├── webhooks.py           # aiohttp: вебхуки платежей + /health
│   ├── utils.py              # утилиты: FFmpeg, base64, директории
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py          # /start, язык, страна, соглашение
│   │   ├── chat.py           # чат: текст, голос, фото, документы + стриминг
│   │   ├── menu.py           # аккаунт, настройки, чаты
│   │   ├── admin.py          # админ-панель
│   │   ├── payments.py       # оплата, транзакции
│   │   └── image_gen.py      # генерация изображений gpt-image-1.5
│   └── locales/
│       ├── __init__.py
│       └── loader.py         # i18n: RU/KZ/UA/EN
├── k8s/
│   ├── namespace.yaml
│   ├── postgres.yaml
│   ├── bot-deployment.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   ├── ingress.yaml
│   └── hpa.yaml
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── requirements.txt
├── schema.sql
├── LICENSE
└── README.md
```

---

## Быстрый запуск (Docker Compose)

### 1. Клонировать репозиторий

```bash
git clone https://github.com/chadoyev/telegram-gpt-provider.git
cd telegram-gpt-provider
```

### 2. Настроить переменные окружения

```bash
cp .env.example .env
# Заполнить .env реальными значениями
```

Обязательные переменные:

| Переменная         | Описание                                        |
| ------------------ | ----------------------------------------------- |
| `API_TOKEN`        | Токен Telegram-бота от @BotFather               |
| `ADMIN_ID`         | Ваш Telegram ID                                 |
| `OPENAI_API_KEY`   | API-ключ OpenAI                                 |
| `DB_PASSWORD`      | Пароль PostgreSQL                                |
| `WEBHOOK_BASE_URL` | Публичный HTTPS-URL сервера (напр. `https://bot.example.com`) |
| `WEBHOOK_SECRET`   | Секретный токен для верификации webhook          |

### 3. Запустить

```bash
docker compose up -d
```

Бот запустится вместе с PostgreSQL. Таблицы создаются автоматически при старте.

### 4. Проверить

```bash
docker compose logs -f bot
# Должно быть: "Webhook server started on 0.0.0.0:8443" и "Telegram webhook set: ..."
```

---

## Запуск без Docker

### Требования

- Python 3.12+
- PostgreSQL 16+
- FFmpeg (в PATH)

### Установка

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### Создать БД

```bash
createdb uai_robot
# Или через psql:
# psql -U postgres -c "CREATE DATABASE uai_robot;"
```

### Запуск

```bash
cp .env.example .env
# Заполнить .env (DB_HOST=127.0.0.1 для локального запуска)

python -m app
```

---

## Деплой в Kubernetes

### 1. Получить Docker-образ

```bash
docker pull chadoyev/uai-robot:latest
```

### 2. Настроить секреты

Отредактируйте `k8s/secrets.yaml` — замените `CHANGE_ME` на реальные значения.

### 3. Применить манифесты

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/bot-deployment.yaml
kubectl apply -f k8s/hpa.yaml
# kubectl apply -f k8s/ingress.yaml  # если нужен Ingress для вебхуков
```

### 4. Проверить

```bash
kubectl -n uai-robot get pods
kubectl -n uai-robot logs -f deployment/uai-robot-bot
```

### Автоскейлинг

HPA настроен на:
- 1–10 реплик
- Скейл по CPU (70%) и памяти (80%)

Бот работает через Telegram Webhook, поэтому горизонтальное масштабирование работает из коробки.

---

## Платёжные системы

Бот поддерживает две платёжные системы:

### Robokassa

1. Зарегистрируйтесь на [robokassa.com](https://robokassa.com)
2. Result URL: `https://your-domain.com/robokassa`
3. Заполните `ROBOKASSA_*` в `.env`

### YooKassa

1. Зарегистрируйтесь на [yookassa.ru](https://yookassa.ru)
2. Webhook URL: `https://your-domain.com/yookassa`
3. Заполните `YOOKASSA_*` в `.env`

---

## Модели OpenAI

| Модель               | Описание                             | Цена API                              |
| -------------------- | ------------------------------------ | ------------------------------------- |
| GPT-5.4 Mini         | Быстрая модель для повседневных задач | $0.75 / $4.50 за 1M токенов          |
| GPT-5.4              | Флагманская модель                   | $2.50 / $15.00 за 1M токенов         |
| gpt-4o-transcribe    | Распознавание речи                   | $0.006 / мин                          |
| gpt-4o-mini-tts      | Озвучивание текста (11 голосов)       | $18 / 1M символов                     |
| gpt-image-1.5        | Генерация изображений                | $0.034 / изображение (1024x1024)      |

### Поддерживаемые форматы файлов

- **Изображения**: JPG, PNG, GIF, WebP
- **Документы**: PDF, DOC, DOCX, PPT, PPTX
- **Таблицы**: CSV, TSV, XLS, XLSX
- **Текст/Код**: TXT, MD, JSON, XML, YAML, PY, JS, TS, HTML, CSS

---

## Переменные окружения

| Переменная          | Обязательная | По умолчанию        | Описание                        |
| ------------------- | ------------ | -------------------- | ------------------------------- |
| `API_TOKEN`         | Да           | —                    | Telegram Bot Token              |
| `ADMIN_ID`          | Да           | 0                    | Telegram ID администратора       |
| `PASSWORD_ADMIN`    | Нет          | Admin                | Пароль для админ-панели          |
| `OPENAI_API_KEY`    | Да           | —                    | API-ключ OpenAI                  |
| `DB_HOST`           | Нет          | postgres             | Хост PostgreSQL                  |
| `DB_PORT`           | Нет          | 5432                 | Порт PostgreSQL                  |
| `DB_USER`           | Нет          | postgres             | Пользователь БД                  |
| `DB_PASSWORD`       | Да           | —                    | Пароль БД                        |
| `DB_NAME`           | Нет          | uai_robot            | Имя БД                           |
| `WEBHOOK_HOST`      | Нет          | 0.0.0.0              | Хост webhook-сервера             |
| `WEBHOOK_PORT`      | Нет          | 8443                 | Порт webhook-сервера             |
| `WEBHOOK_BASE_URL`  | Да           | —                    | Публичный HTTPS-URL (напр. `https://bot.example.com`) |
| `WEBHOOK_SECRET`    | Нет          | —                    | Секрет для верификации Telegram webhook |
| `MESSAGES_DIR`      | Нет          | users                | Директория для файлов            |

---

## Лицензия

MIT — см. файл [LICENSE](LICENSE).
