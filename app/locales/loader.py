from __future__ import annotations
from typing import Any

_STRINGS: dict[str, dict[str, str]] = {
    # ── General ──
    "bot_unavailable": {
        "ru": "Бот временно недоступен!",
        "kz": "Бот уақытша қолжетімсіз!",
        "ua": "Бот тимчасово недоступний!",
        "en": "The bot is temporarily unavailable!",
    },
    "unexpected_error": {
        "ru": "Непредвиденная ошибка! Разработчик скоро это починит!",
        "kz": "Күтпеген қате! Әзірлеуші оны жақын арада түзетеді!",
        "ua": "Непередбачена помилка! Розробник скоро це полагодить!",
        "en": "Unexpected error! The developer will fix it soon!",
    },
    "insufficient_funds": {
        "ru": "Недостаточно средств!",
        "kz": "Қаражат жеткіліксіз!",
        "ua": "Недостатньо коштів!",
        "en": "Insufficient funds!",
    },
    "updating": {
        "ru": "Обновляю...",
        "kz": "Жаңартамын...",
        "ua": "Оновлюю...",
        "en": "Updating...",
    },

    # ── Start / Welcome ──
    "choose_language": {
        "ru": "Выберите язык интерфейса бота:\nБот интерфейсінің тілін таңдаңыз:\nВиберіть мову інтерфейсу бота:\nSelect the bot interface language:",
        "kz": "Выберите язык интерфейса бота:\nБот интерфейсінің тілін таңдаңыз:\nВиберіть мову інтерфейсу бота:\nSelect the bot interface language:",
        "ua": "Выберите язык интерфейса бота:\nБот интерфейсінің тілін таңдаңыз:\nВиберіть мову інтерфейсу бота:\nSelect the bot interface language:",
        "en": "Выберите язык интерфейса бота:\nБот интерфейсінің тілін таңдаңыз:\nВиберіть мову інтерфейсу бота:\nSelect the bot interface language:",
    },
    "choose_country": {
        "ru": "Выберите страну проживания:",
        "kz": "Тұратын елді таңдаңыз:",
        "ua": "Виберіть країну проживання:",
        "en": "Select country of residence:",
    },
    "terms_of_use": {
        "ru": (
            "*Пользовательское соглашение:*\n"
            "_1. Пользователь соглашается на использование бота и понимает, что бот работает через официальный API OpenAI.\n"
            "2. Разработчик не контролирует содержание ответов, скорость и задержки.\n"
            "3. Пользователь использует бота только в законных целях.\n"
            "4. Разработчик не несёт ответственности за убытки от использования бота.\n"
            "5. Разработчик может изменять условия без предварительного уведомления._"
        ),
        "kz": (
            "*Қолдану ережелері:*\n"
            "_1. Пайдаланушы ботты пайдалануға келіседі және бот ресми OpenAI API арқылы жұмыс істейтінін түсінеді.\n"
            "2. Әзірлеуші жауаптардың мазмұнын, жылдамдығын басқармайды.\n"
            "3. Пайдаланушы ботты тек заңды мақсаттарда пайдаланады.\n"
            "4. Әзірлеуші ботты пайдаланудан болған шығынға жауапты емес.\n"
            "5. Әзірлеуші шарттарды алдын ала ескертусіз өзгерте алады._"
        ),
        "ua": (
            "*Угода користувача:*\n"
            "_1. Користувач погоджується на використання бота і розуміє, що бот працює через офіційний API OpenAI.\n"
            "2. Розробник не контролює зміст відповідей, швидкість і затримки.\n"
            "3. Користувач використовує бота лише в законних цілях.\n"
            "4. Розробник не несе відповідальності за збитки від використання бота.\n"
            "5. Розробник може змінювати умови без попереднього повідомлення._"
        ),
        "en": (
            "*Terms of Use:*\n"
            "_1. The user agrees to use the bot and understands it works via the official OpenAI API.\n"
            "2. The developer does not control response content, speed, or delays.\n"
            "3. The user will only use the bot for lawful purposes.\n"
            "4. The developer is not liable for any losses from using the bot.\n"
            "5. The developer may change these terms without prior notice._"
        ),
    },
    "welcome_message": {
        "ru": (
            "*Здравствуйте! Я ИИ-ассистент на базе GPT-5.4.*\n\n"
            "Я умею:\n"
            "- Вести диалог с потоковой передачей ответа\n"
            "- Анализировать фотографии и документы (PDF, DOCX, TXT и др.)\n"
            "- Генерировать изображения (DALL-E 3)\n"
            "- Распознавать и озвучивать голосовые сообщения\n\n"
            "Нажмите *Начать чат* и просто напишите сообщение!"
        ),
        "kz": (
            "*Сәлеметсіз бе! Мен GPT-5.4 негізіндегі ИИ-ассистентпін.*\n\n"
            "Мен біле аламын:\n"
            "- Ағынды жауап беру арқылы диалог жүргізу\n"
            "- Фотосуреттер мен құжаттарды талдау (PDF, DOCX, TXT, т.б.)\n"
            "- Суреттер генерациялау (DALL-E 3)\n"
            "- Дауыстық хабарламаларды тану және озвучить ету\n\n"
            "*Чатты бастау* түймесін басыңыз!"
        ),
        "ua": (
            "*Вітаю! Я ШІ-асистент на базі GPT-5.4.*\n\n"
            "Я вмію:\n"
            "- Вести діалог з потоковою передачею відповіді\n"
            "- Аналізувати фотографії та документи (PDF, DOCX, TXT та ін.)\n"
            "- Генерувати зображення (DALL-E 3)\n"
            "- Розпізнавати та озвучувати голосові повідомлення\n\n"
            "Натисніть *Почати чат* і просто напишіть повідомлення!"
        ),
        "en": (
            "*Hello! I am an AI assistant powered by GPT-5.4.*\n\n"
            "I can:\n"
            "- Chat with streaming responses\n"
            "- Analyze photos and documents (PDF, DOCX, TXT, etc.)\n"
            "- Generate images (DALL-E 3)\n"
            "- Recognize and voice your messages\n\n"
            "Press *Start Chat* and just type your message!"
        ),
    },

    # ── Chat ──
    "thinking": {
        "ru": "Думаю над ответом...",
        "kz": "Жауап ойластырамын...",
        "ua": "Думаю над відповіддю...",
        "en": "Thinking...",
    },
    "chat_started": {
        "ru": "Привет! Жду вашего сообщения.",
        "kz": "Сәлеметсіз бе! Хабарламаңызды күтемін.",
        "ua": "Вітаю! Чекаю на ваше повідомлення.",
        "en": "Hello! Waiting for your message.",
    },
    "chat_ended": {
        "ru": "Чат завершён! Нажмите «Начать чат» для нового.",
        "kz": "Чат аяқталды! Жаңа чат үшін «Чатты бастау» басыңыз.",
        "ua": "Чат завершено! Натисніть «Почати чат» для нового.",
        "en": "Chat ended! Press \"Start Chat\" for a new one.",
    },
    "no_active_chat": {
        "ru": "У вас нет активного чата. Нажмите «Начать чат».",
        "kz": "Белсенді чатыңыз жоқ. «Чатты бастау» басыңыз.",
        "ua": "У вас немає активного чату. Натисніть «Почати чат».",
        "en": "You have no active chat. Press \"Start Chat\".",
    },
    "already_has_chat": {
        "ru": "У вас уже есть активный чат. Завершите его сначала.",
        "kz": "Сізде белсенді чат бар. Алдымен оны аяқтаңыз.",
        "ua": "У вас вже є активний чат. Завершіть його спочатку.",
        "en": "You already have an active chat. End it first.",
    },
    "recognize_voice": {
        "ru": "Расшифровываю голосовое сообщение...",
        "kz": "Дауыстық хабарламаны жазып жатырмын...",
        "ua": "Розшифровую голосове повідомлення...",
        "en": "Transcribing your voice message...",
    },
    "voice_empty": {
        "ru": "Голосовое сообщение не распознано!",
        "kz": "Дауыстық хабар танылмады!",
        "ua": "Голосове повідомлення не розпізнане!",
        "en": "Voice message not recognized!",
    },
    "error_context_overflow": {
        "ru": "Контекст переполнен! Завершите чат и начните новый.",
        "kz": "Контекст толып кетті! Чатты аяқтап, жаңасын бастаңыз.",
        "ua": "Контекст переповнений! Завершіть чат і почніть новий.",
        "en": "Context overflow! End this chat and start a new one.",
    },
    "error_ai_overloaded": {
        "ru": "Нейросеть перегружена, подождите и повторите.",
        "kz": "Нейрожелі шамадан тыс жүктелген, күтіңіз.",
        "ua": "Нейромережа перевантажена, зачекайте і повторіть.",
        "en": "AI is overloaded, please wait and retry.",
    },
    "file_received": {
        "ru": "Файл получен, анализирую...",
        "kz": "Файл алынды, талдаудамын...",
        "ua": "Файл отримано, аналізую...",
        "en": "File received, analyzing...",
    },
    "file_unsupported": {
        "ru": "Этот тип файла не поддерживается. Поддерживаются: PDF, DOCX, TXT, CSV, XLSX, изображения.",
        "kz": "Бұл файл түрі қолдау көрсетілмейді. Қолдау: PDF, DOCX, TXT, CSV, XLSX, суреттер.",
        "ua": "Цей тип файлу не підтримується. Підтримуються: PDF, DOCX, TXT, CSV, XLSX, зображення.",
        "en": "This file type is not supported. Supported: PDF, DOCX, TXT, CSV, XLSX, images.",
    },

    # ── Image generation ──
    "img_gen_prompt": {
        "ru": "Напишите запрос на генерацию изображения.\nМодель: DALL-E 3 | Размер: 1024x1024",
        "kz": "Кескін генерациялау сұрауын жазыңыз.\nМодель: DALL-E 3 | Өлшемі: 1024x1024",
        "ua": "Напишіть запит на генерацію зображення.\nМодель: DALL-E 3 | Розмір: 1024x1024",
        "en": "Write a prompt to generate an image.\nModel: DALL-E 3 | Size: 1024x1024",
    },
    "img_generating": {
        "ru": "Генерирую изображение...",
        "kz": "Кескінді жасап жатырмын...",
        "ua": "Генерую зображення...",
        "en": "Generating image...",
    },
    "img_ready": {
        "ru": "Изображение готово!\nПромпт: `{prompt}`\nРасход: {cost} {cur}\nБаланс: {balance} {cur}",
        "kz": "Сурет дайын!\nСұраныс: `{prompt}`\nТұтыну: {cost} {cur}\nБаланс: {balance} {cur}",
        "ua": "Зображення готове!\nПромпт: `{prompt}`\nВитрата: {cost} {cur}\nБаланс: {balance} {cur}",
        "en": "Image ready!\nPrompt: `{prompt}`\nCost: {cost} {cur}\nBalance: {balance} {cur}",
    },

    # ── Buttons ──
    "btn_account": {"ru": "Аккаунт", "kz": "Аккаунт", "ua": "Акаунт", "en": "Account"},
    "btn_start_chat": {"ru": "Начать чат", "kz": "Чатты бастау", "ua": "Почати чат", "en": "Start Chat"},
    "btn_end_chat": {"ru": "Завершить чат", "kz": "Чатты аяқтау", "ua": "Завершити чат", "en": "End Chat"},
    "btn_generate_image": {"ru": "Генерация изображения", "kz": "Кескінді жасау", "ua": "Генерація зображення", "en": "Generate Image"},
    "btn_top_up": {"ru": "Пополнить баланс", "kz": "Балансты толтыру", "ua": "Поповнити баланс", "en": "Top Up"},
    "btn_change_model": {"ru": "Модель ИИ", "kz": "AI моделі", "ua": "Модель ІІ", "en": "AI Model"},
    "btn_change_voice": {"ru": "Голос ИИ", "kz": "AI дауысы", "ua": "Голос ІІ", "en": "AI Voice"},
    "btn_my_chats": {"ru": "Мои чаты", "kz": "Менің чаттар", "ua": "Мої чати", "en": "My Chats"},
    "btn_transactions": {"ru": "Мои операции", "kz": "Транзакциялар", "ua": "Мої операції", "en": "Transactions"},
    "btn_prices": {"ru": "Наши цены", "kz": "Біздің бағалар", "ua": "Наші ціни", "en": "Our Prices"},
    "btn_support": {"ru": "Поддержка", "kz": "Қолдау", "ua": "Підтримка", "en": "Support"},
    "btn_back": {"ru": "Назад", "kz": "Артқа", "ua": "Назад", "en": "Back"},
    "btn_close": {"ru": "Закрыть", "kz": "Жабу", "ua": "Закрити", "en": "Close"},
    "btn_accept": {"ru": "Принимаю", "kz": "Қабылдаймын", "ua": "Приймаю", "en": "Accept"},
    "btn_change_lang": {"ru": "Изменить язык", "kz": "Тілді өзгерту", "ua": "Змінити мову", "en": "Change Language"},
    "btn_change_country": {"ru": "Изменить страну", "kz": "Елді өзгерту", "ua": "Змінити країну", "en": "Change Country"},
    "btn_voice_on": {"ru": "Включить озвучку", "kz": "Дауысты қосу", "ua": "Увімкнути озвучку", "en": "Voice On"},
    "btn_voice_off": {"ru": "Выключить озвучку", "kz": "Дауысты өшіру", "ua": "Вимкнути озвучку", "en": "Voice Off"},
    "btn_get_all_chats": {"ru": "Все чаты", "kz": "Барлық чаттар", "ua": "Всі чати", "en": "All Chats"},
    "btn_get_chat": {"ru": "Получить чат", "kz": "Чатты алу", "ua": "Отримати чат", "en": "Get Chat"},
    "btn_delete_history": {"ru": "Удалить историю", "kz": "Тарихты жою", "ua": "Видалити історію", "en": "Delete History"},
    "btn_subscribe": {"ru": "Подписаться", "kz": "Жазылу", "ua": "Підписатися", "en": "Subscribe"},

    # ── Menu / Account ──
    "account_info": {
        "ru": (
            "🆔 {user_id} | *{name}*\n"
            "├📅 Регистрация: {date} ({days})\n"
            "├💵 Баланс: {balance} {cur}\n"
            "├🤖 Модель: {model}\n"
            "├🔊 Голос: {voice}\n"
            "├✉ Сообщений: {msgs}\n"
            "├💬 Чатов: {chats}\n"
            "├🌐 Страна: {country}\n"
            "└👥 Рефералов: {refs}\n\n"
            "🔗 Ссылка для друзей: `{ref_link}`"
        ),
        "kz": (
            "🆔 {user_id} | *{name}*\n"
            "├📅 Тіркелу: {date} ({days})\n"
            "├💵 Баланс: {balance} {cur}\n"
            "├🤖 Модель: {model}\n"
            "├🔊 Дауыс: {voice}\n"
            "├✉ Хабарламалар: {msgs}\n"
            "├💬 Чаттар: {chats}\n"
            "├🌐 Ел: {country}\n"
            "└👥 Рефералдар: {refs}\n\n"
            "🔗 Достарға сілтеме: `{ref_link}`"
        ),
        "ua": (
            "🆔 {user_id} | *{name}*\n"
            "├📅 Реєстрація: {date} ({days})\n"
            "├💵 Баланс: {balance} {cur}\n"
            "├🤖 Модель: {model}\n"
            "├🔊 Голос: {voice}\n"
            "├✉ Повідомлень: {msgs}\n"
            "├💬 Чатів: {chats}\n"
            "├🌐 Країна: {country}\n"
            "└👥 Рефералів: {refs}\n\n"
            "🔗 Посилання для друзів: `{ref_link}`"
        ),
        "en": (
            "🆔 {user_id} | *{name}*\n"
            "├📅 Registered: {date} ({days})\n"
            "├💵 Balance: {balance} {cur}\n"
            "├🤖 Model: {model}\n"
            "├🔊 Voice: {voice}\n"
            "├✉ Messages: {msgs}\n"
            "├💬 Chats: {chats}\n"
            "├🌐 Country: {country}\n"
            "└👥 Referrals: {refs}\n\n"
            "🔗 Referral link: `{ref_link}`"
        ),
    },
    "country_changed": {
        "ru": "Страна успешно изменена!",
        "kz": "Ел сәтті өзгертілді!",
        "ua": "Країна успішно змінена!",
        "en": "Country changed successfully!",
    },
    "model_changed": {
        "ru": "Модель ИИ успешно изменена!",
        "kz": "AI моделі сәтті өзгертілді!",
        "ua": "Модель ІІ успішно змінена!",
        "en": "AI model changed successfully!",
    },
    "voice_changed": {
        "ru": "Голос ИИ успешно изменён!",
        "kz": "AI дауысы сәтті өзгертілді!",
        "ua": "Голос ІІ успішно змінено!",
        "en": "AI voice changed successfully!",
    },
    "history_deleted": {
        "ru": "История чатов удалена!",
        "kz": "Чат тарихы жойылды!",
        "ua": "Історія чатів видалена!",
        "en": "Chat history deleted!",
    },
    "select_model": {
        "ru": "Выберите модель ИИ:",
        "kz": "AI моделін таңдаңыз:",
        "ua": "Виберіть модель ІІ:",
        "en": "Select AI model:",
    },
    "select_voice": {
        "ru": "Выберите голос для ИИ:",
        "kz": "AI үшін дауысты таңдаңыз:",
        "ua": "Виберіть голос для ІІ:",
        "en": "Select voice for AI:",
    },

    # ── Payments ──
    "pay_prompt": {
        "ru": "Введите сумму пополнения или выберите:",
        "kz": "Толтыру сомасын енгізіңіз немесе таңдаңыз:",
        "ua": "Введіть суму поповнення або виберіть:",
        "en": "Enter the top-up amount or choose:",
    },
    "pay_description": {
        "ru": "Пополнение баланса в боте",
        "kz": "Боттағы балансты толтыру",
        "ua": "Поповнення балансу в боті",
        "en": "Balance top-up in the bot",
    },
    "pay_success": {
        "ru": "Баланс пополнен на {amount} {cur}!",
        "kz": "Баланс {amount} {cur} толтырылды!",
        "ua": "Баланс поповнено на {amount} {cur}!",
        "en": "Balance topped up by {amount} {cur}!",
    },

    # ── Prices ──
    "prices": {
        "ru": (
            "*Наши тарифы:*\n\n"
            "*GPT-5.4 Mini:*\n"
            "💲 $0.90 / 1M токенов (вход)\n"
            "💲 $5.40 / 1M токенов (выход)\n\n"
            "*GPT-5.4:*\n"
            "💲 $3.00 / 1M токенов (вход)\n"
            "💲 $18.00 / 1M токенов (выход)\n\n"
            "*STT (gpt-4o-mini-transcribe):* $0.0036 / мин\n"
            "*TTS (gpt-4o-mini-tts):* $18 / 1M символов\n"
            "*Генерация изображений (gpt-image-1.5):* $0.041 / шт.\n\n"
            "📎 Файлы (PDF, DOCX, XLSX, TXT, код) — по тарифу выбранной модели."
        ),
        "kz": (
            "*Біздің тарифтер:*\n\n"
            "*GPT-5.4 Mini:*\n"
            "💲 $0.90 / 1M токен (кіріс)\n"
            "💲 $5.40 / 1M токен (шығыс)\n\n"
            "*GPT-5.4:*\n"
            "💲 $3.00 / 1M токен (кіріс)\n"
            "💲 $18.00 / 1M токен (шығыс)\n\n"
            "*STT (gpt-4o-mini-transcribe):* $0.0036 / мин\n"
            "*TTS (gpt-4o-mini-tts):* $18 / 1M таңба\n"
            "*Кескін генерациясы (gpt-image-1.5):* $0.041 / шт.\n\n"
            "📎 Файлдар (PDF, DOCX, XLSX, TXT, код) — таңдалған модель тарифі бойынша."
        ),
        "ua": (
            "*Наші тарифи:*\n\n"
            "*GPT-5.4 Mini:*\n"
            "💲 $0.90 / 1M токенів (вхід)\n"
            "💲 $5.40 / 1M токенів (вихід)\n\n"
            "*GPT-5.4:*\n"
            "💲 $3.00 / 1M токенів (вхід)\n"
            "💲 $18.00 / 1M токенів (вихід)\n\n"
            "*STT (gpt-4o-mini-transcribe):* $0.0036 / хв\n"
            "*TTS (gpt-4o-mini-tts):* $18 / 1M символів\n"
            "*Генерація зображень (gpt-image-1.5):* $0.041 / шт.\n\n"
            "📎 Файли (PDF, DOCX, XLSX, TXT, код) — за тарифом обраної моделі."
        ),
        "en": (
            "*Our Pricing:*\n\n"
            "*GPT-5.4 Mini:*\n"
            "💲 $0.90 / 1M tokens (input)\n"
            "💲 $5.40 / 1M tokens (output)\n\n"
            "*GPT-5.4:*\n"
            "💲 $3.00 / 1M tokens (input)\n"
            "💲 $18.00 / 1M tokens (output)\n\n"
            "*STT (gpt-4o-mini-transcribe):* $0.0036 / min\n"
            "*TTS (gpt-4o-mini-tts):* $18 / 1M chars\n"
            "*Image Generation (gpt-image-1.5):* $0.041 / image\n\n"
            "📎 Files (PDF, DOCX, XLSX, TXT, code) — billed per selected model rates."
        ),
    },

    # ── Admin ──
    "admin_menu_title": {
        "ru": "Админ-панель:", "kz": "Админ-панель:", "ua": "Адмін-панель:", "en": "Admin Panel:",
    },
    "admin_enter_password": {
        "ru": "Введите пароль администратора:", "kz": "Әкімші құпия сөзін енгізіңіз:",
        "ua": "Введіть пароль адміністратора:", "en": "Enter admin password:",
    },
    "admin_wrong_password": {
        "ru": "Неверный пароль!", "kz": "Қате құпия сөз!", "ua": "Невірний пароль!", "en": "Wrong password!",
    },
    "admin_broadcast_prompt": {
        "ru": "Введите текст рассылки:", "kz": "Тарату мәтінін енгізіңіз:",
        "ua": "Введіть текст розсилки:", "en": "Enter broadcast message:",
    },
    "admin_broadcast_done": {
        "ru": "Рассылка отправлена {count} пользователям.",
        "kz": "Тарату {count} пайдаланушыға жіберілді.",
        "ua": "Розсилку надіслано {count} користувачам.",
        "en": "Broadcast sent to {count} users.",
    },

    # ── Spending info ──
    "spending_line": {
        "ru": "\n─────────\nТокены: {tokens} | Расход: {cost} {cur} | Баланс: {balance} {cur}",
        "kz": "\n─────────\nТокендер: {tokens} | Шығын: {cost} {cur} | Баланс: {balance} {cur}",
        "ua": "\n─────────\nТокени: {tokens} | Витрата: {cost} {cur} | Баланс: {balance} {cur}",
        "en": "\n─────────\nTokens: {tokens} | Cost: {cost} {cur} | Balance: {balance} {cur}",
    },
}


def t(key: str, lang: str = "en", **kwargs: Any) -> str:
    entry = _STRINGS.get(key, {})
    text = entry.get(lang, entry.get("en", f"[{key}]"))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def get_locale_text(key: str, lang: str = "en", **kwargs: Any) -> str:
    return t(key, lang, **kwargs)
