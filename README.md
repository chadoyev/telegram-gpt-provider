# UAI Robot — Telegram-бот с доступом к ChatGPT

Продвинутый Telegram-бот, который предоставляет пользователям платный доступ к ChatGPT и другим моделям OpenAI.
Поддерживает **текст**, **голос (Whisper + TTS)**, **анализ изображений**, **генерацию картинок (DALL-E 3)**, **историю чатов**, **многоязычный интерфейс (RU/KZ/UA/EN)** и встроенную **платёжную систему** (FreeKassa, Robokassa, YooKassa).

---

## Возможности

- **GPT-4-Turbo / GPT-3.5-Turbo** — текстовый чат с учётом контекста
- **Whisper** — распознавание голосовых сообщений
- **TTS-1** — озвучивание ответов (6 голосов на каждый язык)
- **DALL-E 3** — генерация изображений по промпту
- **GPT-4-Turbo Vision** — анализ фотографий
- **Биллинг** — баланс, пополнение, транзакции, тарификация по токенам
- **Рефералка** — реферальные бонусы, триал, кэшбэк
- **Экспорт** — чаты и транзакции в HTML-файлы
- **Админ-панель** — управление ботом прямо из Telegram
- **Подписка на канал** — опциональная проверка подписки

---

## Технологии

| Компонент | Стек |
|-----------|------|
| Язык | Python 3.10+ |
| Telegram | `pyTelegramBotAPI` (`telebot`) |
| OpenAI | `openai` (Chat, Whisper, TTS, DALL-E) |
| Web / платежи | `Flask` (вебхуки для платёжных коллбэков) |
| База данных | PostgreSQL + `psycopg2-binary` |
| Платежи | FreeKassa, Robokassa, `yookassa` |
| Аудио | FFmpeg (конвертация MP3 ↔ OGG) |
| Прочее | `tiktoken`, `mutagen`, `schedule`, `requests`, `python-dotenv` |

---

## Требования

- **Python** 3.10 или выше
- **PostgreSQL** 12 или выше
- **FFmpeg** (с `ffmpeg.exe` в PATH или в `ffmpeg/bin/`)
- SSL-сертификат (для HTTPS-коллбэков платёжных систем)

---

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/your-username/uai_robot.git
cd uai_robot
```

### 2. Создать виртуальное окружение

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Установить FFmpeg

FFmpeg нужен для конвертации аудио между MP3 и OGG (голосовые сообщения Telegram).

**Windows:**
1. Скачайте [FFmpeg](https://ffmpeg.org/download.html) (builds от gyan.dev или BtbN)
2. Распакуйте и поместите `ffmpeg.exe` в папку `ffmpeg/bin/` внутри проекта
3. Либо добавьте FFmpeg в системный PATH

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

> **Примечание:** В `main.py` путь к ffmpeg прописан как `ffmpeg\bin\ffmpeg.exe`. На Linux/macOS замените на `ffmpeg` (из PATH) или на соответствующий путь.

### 5. Настроить PostgreSQL

1. Установите PostgreSQL, если его ещё нет
2. Создайте базу данных:

```bash
psql -U postgres
```

```sql
CREATE DATABASE uai_robot;
\q
```

3. Инициализируйте таблицы:

```bash
psql -U postgres -d uai_robot -f schema.sql
```

### 6. Создать Telegram-бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot` и следуйте инструкциям
3. Скопируйте полученный **API токен**
4. Запомните ваш **Telegram ID** (можно узнать через [@userinfobot](https://t.me/userinfobot)) — он будет `ADMIN_ID`

### 7. Настроить платёжные системы (опционально)

Бот поддерживает три платёжные системы. Настройте те, которые вам нужны:

**FreeKassa:**
1. Зарегистрируйтесь на [freekassa.com](https://freekassa.com)
2. Создайте магазин, получите `MERCHANT_ID`, `SECRET1`, `SECRET2`
3. Укажите URL уведомления: `https://ваш-сервер:443/freekassa`

**Robokassa:**
1. Зарегистрируйтесь на [robokassa.com](https://robokassa.com)
2. Создайте магазин, получите `LOGIN`, `PASS1`, `PASS2`
3. Укажите Result URL: `https://ваш-сервер:443/robokassa`

**YooKassa:**
1. Зарегистрируйтесь на [yookassa.ru](https://yookassa.ru)
2. Получите `ACCOUNT_ID` и `SECRET_KEY`
3. Настройте вебхук на `https://ваш-сервер:443/yookassa`

### 8. SSL-сертификат

Flask-сервер для приёма платежных коллбэков запускается с HTTPS (порт 443). Вам нужен SSL-сертификат:

**Self-signed (для тестирования):**
```bash
openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes
```

**Production:**
Используйте [Let's Encrypt](https://letsencrypt.org/) (certbot) или сертификат от вашего хостинг-провайдера. Положите файлы `server.crt` и `server.key` в корень проекта.

> Файлы `server.crt` и `server.key` добавлены в `.gitignore` — они **не должны** попадать в репозиторий.

### 9. Настроить переменные окружения

Скопируйте `.env.example` в `.env` и заполните реальными значениями:

```bash
cp .env.example .env
```

Откройте `.env` и заполните:

```dotenv
# === Telegram ===
API_TOKEN=123456789:ABCDefGHIjklMNOpqrSTUvwxyz       # токен от @BotFather
ADMIN_ID=123456789                                     # ваш Telegram ID
PASSWORD_ADMIN=ваш-надёжный-пароль                     # пароль для админ-панели

# === OpenAI ===
OPENAI_API_KEY_PAID=sk-xxxxxxxxxxxxxxxxxxxxxxxx        # API-ключ OpenAI (платная модель)
OPENAI_API_KEY_FREE=sk-xxxxxxxxxxxxxxxxxxxxxxxx        # API-ключ для бесплатной модели (или тот же)
OPENAI_API_BASE_PAID=https://api.openai.com/v1/        # базовый URL OpenAI API
OPENAI_API_BASE_FREE=https://api.openai.com/v1/        # или прокси-сервер

# === FreeKassa ===
FREEKASSA_SECRET1=ваш-секрет-1
FREEKASSA_SECRET2=ваш-секрет-2
FREEKASSA_MERCHANT_ID=123456
FREEKASSA_IP_SERVER=0.0.0.0                            # IP вашего сервера

# === Robokassa ===
ROBOKASSA_LOGIN=ваш-логин
ROBOKASSA_PASS_TEST1=ваш-пароль-1
ROBOKASSA_PASS_TEST2=ваш-пароль-2

# === YooKassa ===
YOOKASSA_ACCOUNT_ID=123456
YOOKASSA_SECRET_KEY=live_xxxxxxxxxxxxxxxxxxxxxxxx
RECEIPT_EMAIL=receipt@yourdomain.com                    # email для чеков YooKassa

# === База данных ===
DB_HOST=127.0.0.1
DB_USER=postgres
DB_PASSWORD=ваш-пароль-от-бд
DB_NAME=uai_robot

# === Ссылки ===
URL_SUPPORT=https://t.me/your_support_bot
URL_BOT=https://t.me/your_bot
URL_CHANNEL=https://t.me/your_channel

# === Прочее ===
MESSAGES_DIR=users                                     # папка для экспорта чатов
```

### 10. Запустить бота

```bash
python main.py
```

Бот запускает **три потока**:
1. **Telegram polling** — приём сообщений от пользователей
2. **Flask HTTPS-сервер** — приём коллбэков от платёжных систем (порт 443)
3. **Scheduler** — фоновые задачи (обновление курсов валют, очистка чатов)

---

## Структура проекта

```
uai_robot/
├── main.py              # основной файл: бот + Flask + БД + платежи
├── config.py            # конфигурация из env-переменных + тексты UI
├── schema.sql           # SQL-схема для инициализации БД
├── requirements.txt     # Python-зависимости
├── .env.example         # шаблон переменных окружения
├── .gitignore
├── LICENSE
├── README.md
├── server.crt           # SSL-сертификат (не в git!)
├── server.key           # SSL-ключ (не в git!)
├── users/               # экспортированные чаты/транзакции (runtime, не в git)
└── ffmpeg/
    └── bin/
        └── ffmpeg.exe   # исполняемый файл FFmpeg (скачать отдельно)
```

---

### Быстрый деплой на Ubuntu

```bash
# 1. Обновить систему
sudo apt update && sudo apt upgrade -y

# 2. Установить зависимости
sudo apt install python3 python3-pip python3-venv postgresql ffmpeg -y

# 3. Настроить PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE uai_robot;"
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'ваш-пароль';"
sudo -u postgres psql -d uai_robot -f schema.sql

# 4. Клонировать проект
git clone https://github.com/your-username/uai_robot.git
cd uai_robot

# 5. Настроить окружение
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Создать .env (заполнить по аналогии с .env.example)
cp .env.example .env
nano .env

# 7. Создать SSL-сертификат (или использовать Let's Encrypt)
openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes

# 8. Запустить
python main.py
```

### Запуск как systemd-сервис (чтобы бот работал постоянно)

Создайте файл `/etc/systemd/system/uai-robot.service`:

```ini
[Unit]
Description=UAI Robot Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/uai_robot
Environment=PATH=/path/to/uai_robot/venv/bin:$PATH
ExecStart=/path/to/uai_robot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable uai-robot
sudo systemctl start uai-robot

# Проверить статус
sudo systemctl status uai-robot

# Смотреть логи
journalctl -u uai-robot -f
```

---

## Лицензия

Смотри файл [LICENSE](LICENSE).
