import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional; in production you can use real env vars
    pass

API_TOKEN = os.getenv("API_TOKEN")  # токен телеграм-бота
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# OpenAI / нейросети
token = os.getenv("OPENAI_API_KEY_PAID")
token_free = os.getenv("OPENAI_API_KEY_FREE")
paid_api = os.getenv("OPENAI_API_BASE_PAID", "https://api.openai.com/v1/")
free_api = os.getenv("OPENAI_API_BASE_FREE", "https://neuroapi.host/v1/")

channel_username = ""
MESSAGES_DIR = os.getenv("MESSAGES_DIR", "users")
password_admin = os.getenv("PASSWORD_ADMIN", "Admin")
system_prompt_paid = 'You are a paid helpful assistant in a telegram bot (@uai_robot). You are communicating with a user. The maximum length of one answer to a user question is 3920 characters. Consider the maximum length when creating large user responses. If your generated answer is too long, then warn the user so that if something happens, he asks for the rest. You can answer questions by text or generate a voice message with an answer, you can receive text messages, voice messages, and you can also understand the contents of photos. You have functionality for generating images, but to generate them: the user must end this chat and click the image generation button. Your services are paid!! Because you are a bot that communicates with users in the Telegram messenger, and your content is generated through the official paid API. That is why you are a paid useful assistant in a telegram bot.'
system_prompt_free = 'You are a paid helpful assistant in the telegram bot. You are communicating with a user. The maximum length of one answer to a user question is 3920 characters. Consider the maximum length when creating large user responses. If your generated answer is too long, then warn the user so that if something happens, he asks for the rest. You can answer questions by text or generate a voice message with an answer, you can receive text messages, voice messages, and you can also understand the contents of photos. You have functionality for generating images, but to generate them: the user must end this chat and click the image generation button. Your services are paid!! Because you are a bot that communicates with users in the Telegram messenger, and your content is generated through the official paid API. That is why you are a paid useful assistant in a telegram bot.'
# FreeKassa
secret_payment1 = os.getenv("FREEKASSA_SECRET1")  # секретное слово1 для кассы
secret_payment2 = os.getenv("FREEKASSA_SECRET2")  # секретное слово2 для кассы
merchant_id = os.getenv("FREEKASSA_MERCHANT_ID")  # id кассы
ip_server = os.getenv("FREEKASSA_IP_SERVER")
ips = [] #payment server ips
# Robokassa
MerchantLogin = os.getenv("ROBOKASSA_LOGIN")
pass_test1 = os.getenv("ROBOKASSA_PASS_TEST1")
pass_test2 = os.getenv("ROBOKASSA_PASS_TEST2")

# YooKassa
account_id = os.getenv("YOOKASSA_ACCOUNT_ID")
secret_key = os.getenv("YOOKASSA_SECRET_KEY")

# database
host = os.getenv("DB_HOST", "127.0.0.1")
user = os.getenv("DB_USER", "postgres")
password = os.getenv("DB_PASSWORD")
db = os.getenv("DB_NAME", "db")


url_support = os.getenv("URL_SUPPORT", "https://t.me/")
url_bot = os.getenv("URL_BOT", "https://t.me/")
url_channel = os.getenv("URL_CHANNEL", "https://t.me/")

politika_confedence = ''

voice_lng_ru = {
    'alloy': 'Алиса',
    'echo': 'Андрей',
    'fable': 'Дмитрий',
    'onyx': 'Тимофей',
    'nova': 'Вероника',
    'shimmer': 'Анастасия'
}
voice_lng_kz = {
    'alloy': 'Адель',
    'echo': 'Айдар',
    'fable': 'Дамир',
    'onyx': 'Тамерлан',
    'nova': 'Асель',
    'shimmer': 'Әлия'
}
voice_lng_ua = {
    'alloy': 'Аліса',
    'echo': 'Андрій',
    'fable': 'Дмитро',
    'onyx': 'Тимофій',
    'nova': 'Вероніка',
    'shimmer': 'Анастасія'
}
voice_lng_en = {
    'alloy': 'Alloy',
    'echo': 'Echo',
    'fable': 'Fable',
    'onyx': 'Onyx',
    'nova': 'Nova',
    'shimmer': 'Shimmer'
}

voice_ai_ru = ['voice_ru/Алиса.mp3',
               'voice_ru/Андрей.mp3',
               'voice_ru/Дмитрий.mp3',
               'voice_ru/Тимофей.mp3',
               'voice_ru/Вероника.mp3',
               'voice_ru/Анастасия.mp3']
voice_ai_kz = ['voice_kz/Адель.mp3',
               'voice_kz/Айдар.mp3',
               'voice_kz/Дамир.mp3',
               'voice_kz/Тамерлан.mp3',
               'voice_kz/Асель.mp3',
               'voice_kz/Әлия.mp3']
voice_ai_ua = ['voice_ua/Аліса.mp3',
               'voice_ua/Андрій.mp3',
               'voice_ua/Дмитро.mp3',
               'voice_ua/Тимофій.mp3',
               'voice_ua/Вероніка.mp3',
               'voice_ua/Анастасія.mp3']
voice_ai_en = ['voice_en/Alloy.mp3',
               'voice_en/Echo.mp3',
               'voice_en/Fable.mp3',
               'voice_en/Onyx.mp3',
               'voice_en/Nova.mp3',
               'voice_en/Shimmer.mp3']

use_gpt4_ru = "❌Загрузка изображений поддерживается только в модели GPT-4-TURBO!\n" \
              "⚙️Смените модель в меню вашего аккаунта!"
use_gpt4_kz = "❌Суреттерді жүктеу тек GPT-4-TURBO үлгісінде жүзеге асырылады!\n" \
              "⚙️Тіркелгі мәзірінде үлгіні өзгертіңіз!"
use_gpt4_ua = "❌Завантаження зображень здійснюється лише у моделі GPT-4-TURBO!\n" \
              "⚙️Змініть модель у меню вашого облікового запису!"
use_gpt4_en = "❌Uploading images is carried out only in the GPT-4-TURBO model!\n" \
              "⚙️Change the model in your account menu!"

chats_menu_text_ru = '⚙Выберите действие:'
chats_menu_text_kz = '⚙Әрекетті таңдаңыз:'
chats_menu_text_ua = '⚙Виберіть дію:'
chats_menu_text_en = '⚙Choose an action:'

chat_input_text_ru = '🔢Введите номер чата, который хотите получить'
chat_input_text_kz = '🔢Алғыңыз келетін чат нөмірін енгізіңіз'
chat_input_text_ua = '🔢Введіть номер чату, який бажаєте отримати'
chat_input_text_en = '🔢Enter the chat number you want to receive'

your_chat_one_ru = '📁Файл с вашим чатом'
your_chat_one_kz = '📁Чатыңызбен файл жасаңыз'
your_chat_one_ua = '📁Файл із вашим чатом.'
your_chat_one_en = '📁The file with your chat.'

delete_history_complete_ru = '✅История чатов успешно удалена!'
delete_history_complete_kz = '✅Чат тарихы сәтті жойылды!'
delete_history_complete_ua = '✅Історія чатів успішно видалена!'
delete_history_complete_en = '✅Chat history successfully deleted!'

error_get_chat_text_ru = '⚠️Произошла ошибка при поиска чата, ввёденное значение должно быть целым числом и больше нуля!'
error_get_chat_text_kz = '⚠️Сөйлесуді іздеу кезінде қате орын алды, енгізілген мән бүтін және нөлден үлкен болуы керек!'
error_get_chat_text_ua = '⚠️Відбулася помилка при пошуку чату, введене значення має бути цілим числом і більше від нуля!'
error_get_chat_text_en = '⚠️An error occurred while searching for a chat, the entered value must be an integer and greater than zero!'

voice_select_menu_ru = '🔊Выберите голос для ИИ:'
voice_select_menu_kz = '🔊AI үшін дауысты таңдаңыз:'
voice_select_menu_ua = '🔊Виберіть голос для ІІ:'
voice_select_menu_en = '🔊Select voice for AI:'

subscribe_invite_ru = 'ℹЧтобы пользоваться ботом, подпишитесь на канал'
subscribe_invite_kz = 'ℹБотты пайдалану үшін арнаға жазылыңыз'
subscribe_invite_ua = 'ℹЩоб користуватися ботом, підпишіться на канал'
subscribe_invite_en = 'ℹTo use the bot, subscribe to the channel'

voice_message_ru = '[Голосовое сообщение]:'
voice_message_kz = '[Дауыстық хабарлама]:'
voice_message_ua = '[Голосове повідомлення]:'
voice_message_en = '[Voice message]:'

voice_empty_ru = '❌Голосовое сообщение не распознано!'
voice_empty_kz = '❌Дауыстық хабар танылмады!'
voice_empty_ua = '❌Голосове повідомлення не розпізнане!'
voice_empty_en = '❌Voice message not recognized!'

recognize_voice_ru = '🗣👂Расшифровываю ваше голосовое сообщение...'
recognize_voice_kz = '🗣👂Мен сіздің дауыстық хабарламаңызды жазып жатырмын...'
recognize_voice_ua = '🗣👂Розшифровую ваше голосове повідомлення...'
recognize_voice_en = '🗣👂I am transcribing your voice message...'

pay_desc_ru = 'Пополнение баланса в боте @uai_robot'
pay_desc_kz = '@uai_robot ботындағы балансты толтыру'
pay_desc_ua = 'Поповнення балансу в роботі @uai_robot'
pay_desc_en = 'Replenishment of the balance in the @uai_robot bot'

change_ai_model_ru = "🤖Выберете нейросеть из предложенных вариантов:\n" \
                     "📰Статья о сравнении этих двух моделей: [клик](https://teletype.in/@uai_robot/gpt-ru)"
change_ai_model_kz = "🤖Ұсынылған опциялардан нейрондық желіні таңдаңыз:\n" \
                     "📰Осы екі модельді салыстыру туралы мақала: [басыңыз](https://teletype.in/@uai_robot/gpt-kz)"
change_ai_model_ua = "🤖Виберіть нейромережу із запропонованих варіантів:\n" \
                     "📰Стаття для порівняння цих двох моделей: [клік](https://teletype.in/@uai_robot/gpt-ua)"
change_ai_model_en = "🤖Select a neural network from the proposed options:\n" \
                     "📰Article about comparison of these two models: [click](https://teletype.in/@uai_robot/gpt-en)"

error_openai_ru = "❌Нейросеть не может сгенерировать ответ, так как превышено количество обрабатываемой информации!\n" \
                   "Завершите этот чат и начните новый!"
error_openai_kz = "❌Нейрондық желі жауап бере алмайды, себебі өңделетін ақпарат мөлшерінен асып кетті!\n" \
                  "Осы чатты аяқтап, жаңасын бастаңыз!"
error_openai_ua = "❌Нейросеть не може згенерувати відповідь, оскільки перевищено кількість інформації, що обробляється!\n" \
                  "Завершіть цей чат та почніть новий!"
error_openai_en = "❌The neural network cannot generate a response because the amount " \
                  "of information being processed has been exceeded!\nEnd this chat and start a new one!"

error_openai_load_ru = '❌Нейросеть перегружена, подождите немного и задайте снова этот же вопрос не завершая текущий чат!'
error_openai_load_kz = '❌Нейрондық желі шамадан тыс жүктелген, сәл күте тұрыңыз және ағымдағы чатты аяқтамай, сол сұрақты қайта қойыңыз!'
error_openai_load_ua = '❌Нейросітка перевантажена, зачекайте трохи і задайте знову це питання не завершуючи поточний чат!'
error_openai_load_en = '❌The neural network is overloaded, please wait a bit and ask the same question again without ending the current chat!'

error_unkown_ru = "❌Непредвиденная ошибка! Разработчик скоро это починит!"
error_unkown_kz = "❌Күтпеген қате! Әзірлеуші оны жақын арада түзетеді!"
error_unkown_ua = "❌Непередбачена помилка! Розробник скоро це полагодить!"
error_unkown_en = "❌Unexpected error! Developer will fix it soon!"

error_unkown2_ru = "❌Непредвиденная ошибка!"
error_unkown2_kz = "❌Күтпеген қате!"
error_unkown2_ua = "❌Непередбачена помилка!"
error_unkown2_en = "❌Unexpected error!"

error_money_ru = '❌Недостаточно средств!'
error_money_kz = '❌Қаражат жеткіліксіз!'
error_money_ua = '❌Недостатньо коштів!'
error_money_en = '❌Insufficient funds!'

price_ru = '🚀 *Наши Тарифы:*\n\n' \
           '1️⃣*GPT-4-Turbo:*\n' \
           '💲 0.04$ за 1000 токенов входных данных.\n' \
           '💲 0.07$ за 1000 токенов выходных данных.\n\n' \
           '2️⃣*GPT-3.5-Turbo:*\n' \
           '💲 0.002$ за 1000 токенов входных данных.\n' \
           '💲 0.0025$ за 1000 токенов выходных данных.\n\n' \
           '3️⃣*Whisper:*\n' \
           '💲 0.008$ за 1 минуту голосового сообщения.\n\n' \
           '4️⃣*TTS-1:*\n' \
           '💲 0.045$ за 1000 символов озвучиваемого текста.\n\n' \
           '5️⃣*DALL-E-3:*\n' \
           '💲 0.1$ за одно сгенерированное изображение.\n\n' \
           '❓ *Как работает наша система?*\n' \
           '🤖 *GPT-4-Turbo и GPT-3.5-Turbo* - это передовые модели искусственного интеллекта, которые помогут вам получить ответы на ваши вопросы, написать тексты и многое другое. Оплата взимается за количество обрабатываемых слов (токенов).\n' \
           '🎧 *Whisper* - эта модель преобразует ваше голосовое сообщение в текст, который затем обрабатывается моделями GPT для создания ответа.\n' \
           '🔊*TTS-1* - превращает текстовые ответы от GPT-моделей в натуральное звучащее голосовое сообщение.\n' \
           '🎨 DALL-E-3 - создает уникальные изображения по вашему запросу. Отлично подходит для визуализации идей и концепций!'
price_kz = '🚀 *Біздің Тарифтер:*\n\n' \
           '1️⃣ *GPT-4-Turbo:*\n' \
           '💲 0.04$ 1000 токен кіріс деректері үшін.\n' \
           '💲 0.07$ 1000 токен шығыс деректері үшін.\n\n' \
           '2️⃣ *GPT-3.5-Turbo:*\n' \
           '💲 0.002$ 1000 токен кіріс деректері үшін.\n' \
           '💲 0.0025$ 1000 токен шығыс деректері үшін.\n\n' \
           '3️⃣ *Whisper:*\n' \
           '💲 0.008$ дауыстық хабарламаға 1 минут үшін.\n\n' \
           '4️⃣ *TTS-1:*\n' \
           '💲 0.045$ дауысталатын мәтіннің 1000 таңбасы үшін.\n\n' \
           '5️⃣ *DALL-E-3:*\n' \
           '💲 0.1$ әрбір жасалған сурет үшін.\n\n' \
           '❓*Біздің жүйе қалай жұмыс істейді?*\n' \
           '🤖 *GPT-4-Turbo және GPT-3.5-Turbo* - бұл жетекші жасанды интеллект модельдері, сізге сұрақтарыңызға жауап алуға, мәтіндер жазуға және басқа да көптеген нәрселерге көмектеседі. Төлем сөздер санына (токендер) байланысты алынады.\n' \
           '🎧 *Whisper* - бұл модель сіздің дауыстық хабарламаңызды мәтінге айналдырады, содан кейін GPT модельдері оны өңдеп, жауап жасайды.\n' \
           '🔊 *TTS-1* - GPT модельдерінің мәтіндік жауаптарын табиғи дыбыстағы дауыстық хабарламаға айналдырады.\n' \
           '🎨 *DALL-E-3* - сіздің сұрауыңыз бойынша бірегей суреттер жасайды. Идеялар мен түсініктерді визуализациялау үшін тамаша!'
price_ua = '🚀 *Наші Тарифи:*\n\n' \
           '1️⃣ *GPT-4-Turbo:*\n' \
           '💲 0.04$ за 1000 токенів вхідних даних.\n' \
           '💲 0.07$ за 1000 токенів вихідних даних.\n\n' \
           '2️⃣ *GPT-3.5-Turbo:*\n' \
           '💲 0.002$ за 1000 токенів вхідних даних.\n' \
           '💲 0.0025$ за 1000 токенів вихідних даних.\n\n' \
           '3️⃣ *Whisper:*\n' \
           '💲 0.008$ за 1 хвилину голосового повідомлення.\n\n' \
           '4️⃣ *TTS-1:*\n' \
           '💲 0.045$ за 1000 символів озвучуваного тексту.\n\n' \
           '5️⃣ *DALL-E-3:*\n' \
           '💲 0.1$ за кожне згенероване зображення.\n\n' \
           '❓ *Як працює наша система?*\n' \
           '🤖 *GPT-4-Turbo та GPT-3.5-Turbo* - це передові моделі штучного інтелекту, які допоможуть вам отримати відповіді на ваші запитання, написати тексти та багато іншого. Оплата стягується за кількість оброблюваних слів (токенів).\n' \
           '🎧 *Whisper* - ця модель перетворює ваше голосове повідомлення на текст, який потім обробляється моделями GPT для створення відповіді.\n' \
           '🔊 *TTS-1* - перетворює текстові відповіді від моделей GPT у природно звучаще голосове повідомлення.\n' \
           '🎨 *DALL-E-3* - створює унікальні зображення за вашим запитом. Чудово підходить для візуалізації ідей та концепцій!'
price_en = '🚀 *Our Tariffs:*\n\n' \
           '1️⃣ *GPT-4-Turbo:*\n' \
           '💲 0.04$ per 1000 tokens of input data.\n' \
           '💲 0.07$ per 1000 tokens of output data.\n\n' \
           '2️⃣ *GPT-3.5-Turbo:*\n' \
           '💲 0.002$ per 1000 tokens of input data.\n' \
           '💲 0.0025$ per 1000 tokens of output data.\n\n' \
           '3️⃣ *Whisper:*\n' \
           '💲 0.008$ per 1 minute of voice message.\n\n' \
           '4️⃣ *TTS-1:*\n' \
           '💲 0.045$ per 1000 characters of voiced text.\n\n' \
           '5️⃣ *DALL-E-3:*\n' \
           '💲 0.1$ per generated image.\n\n' \
           '❓*How does our system work?*\n' \
           '🤖 *GPT-4-Turbo and GPT-3.5-Turbo* - these are advanced artificial intelligence models that will help you get answers to your questions, write texts, and much more. Payment is charged based on the number of processed words (tokens).\n' \
           '🎧 *Whisper* - this model converts your voice message into text, which is then processed by GPT models to create a response.\n' \
           '🔊 *TTS-1* - converts text responses from GPT models into a natural sounding voice message.\n' \
           '🎨 *DALL-E-3* - creates unique images based on your request. Great for visualizing ideas and concepts!'

rashod_ru = "\n\n=================\nРасходы:\n🎙️Расшифровка: 0 {}\n🔊 Озвучивание: 0 {}\n🏷Токены: 0 ~ 0 {}\n💸Потрачено: 0 {}\n💰Баланс: 0 {}"
rashod_kz = "\n\n=================\nШығындар:\n🎙️Декодтау: 0 {}\n🔊 Дауысты орындау: 0 {}\n🏷Токендер: 0 ~ 0 {}\n💸Жұмсалған: 0 {}\n💰Баланс: 0 {}"
rashod_ua = "\n\n=================\nВитрати:\n🎙️Розшифрування: 0 {}\n🔊️Озвучування: 0 {}\n🏷Токени: 0 ~ 0 {}\n💸Витрачено: 0 {}\n💰Баланс: 0 {}"
rashod_en = "\n\n=================\nExpenses:\n🎙️Decoding: 0 {}\n🔊️Voice acting: 0 {}\n🏷Tokens: 0 ~ 0 {}\n💸Spent: 0 {}\n💰Balance: 0 {}"

error_text_msg_ru = '❌Вы не начали чат, нажмите кнопку\n"🟢Начать чат"'
error_text_msg_kz = '❌Сіз чатты бастамадыңыз, \n«🟢Чатты бастау» түймесін басыңыз'
error_text_msg_ua = '❌Ви не почали чат, натисніть кнопку \n"🟢Почати чат"'
error_text_msg_en = '❌You have not started a chat, \nclick the "🟢Start chat" button'

error_delete_msg_ru = '❌Не удалось удалить сообщение! Удалите вручную!'
error_delete_msg_kz = '❌Хабарды жою мүмкін болмады! Қолмен алып тастаңыз!'
error_delete_msg_ua = '❌Неможливо видалити повідомлення! Видаліть вручну!'
error_delete_msg_en = '❌Failed to delete message! Remove manually!'

chat_end_text_ru = 'ℹЧат завершён! Чтобы начать новый чат, нажмите кнопку "Начать чат"'
chat_end_text_kz = 'ℹЧат аяқталды! Жаңа чатты бастау үшін «Чатты бастау» түймесін басыңыз'
chat_end_text_ua = 'ℹЧат завершено! Щоб розпочати новий чат, натисніть кнопку "Почати чат"'
chat_end_text_en = 'ℹChat is over! To start a new chat, click the "Start Chat" button'

process_file_operation_ru = '⚙Собираю информацию о ваших операциях...'
process_file_operation_kz = '⚙Мен сіздің операцияларыңыз туралы ақпаратты жинап жатырмын...'
process_file_operation_ua = '⚙Збираю інформацію про ваші операції...'
process_file_operation_en = "⚙I'm collecting information about your operations..."

process_file_chats_ru = '⚙Собираю информацию о ваших чатах...'
process_file_chats_kz = '⚙Мен сіздің чаттарыңыз туралы ақпаратты жинап жатырмын...'
process_file_chats_ua = '⚙Збираю інформацію про ваші чати...'
process_file_chats_en = "⚙I'm collecting information about your chats..."

your_chat_ru = '📁Файл с вашим завершенным чатом'
your_chat_kz = '📁Аяқталған чатпен файлды сақтаңыз.'
your_chat_ua = '📁Файл із вашим завершеним чатом.'
your_chat_en = '📁The file with your completed chat.'

your_chats_ru = '📁Файл с вашими завершенными чатами'
your_chats_kz = '📁Аяқталған чаттарыңызбен файлды сақтаңыз'
your_chats_ua = '📁Файл із завершеними чатами'
your_chats_en = '📁File with your completed chats'

your_transactions_ru = '📁Файл с вашими транзакциями.'
your_transactions_kz = '📁Транзакцияларыңызбен файл жасаңыз.'
your_transactions_ua = '📁Файл із транзакціями.'
your_transactions_en = '📁File with your transactions.'


error_create_chat_ru = "❌Невозможно начать новый чат, т.к у вас уже есть активный чат.\nЗавершите его, и начните новый"
error_create_chat_kz = "❌Жаңа чатты бастау мүмкін емес, себебі сізде белсенді чат бар.\nОны аяқтап, жаңасын бастаңыз"
error_create_chat_ua = "❌Неможливо розпочати новий чат, тому що у вас є активний чат.\nЗавершіть його і почніть новий"
error_create_chat_en = "❌Unable to start a new chat because you already have an active chat.\nEnd it and start a new one"

bot_out_ru = '⚙Бот временно недоступен!'
bot_out_kz = '⚙Бот уақытша қолжетімсіз!'
bot_out_ua = '⚙Бот тимчасово недоступний!'
bot_out_en = '⚙The bot is temporarily unavailable!'

wait_msg_ru = "♻ Я думаю что ответить на твоё сообщение..."
wait_msg_kz = "♻ Мен сіздің постыңызға жауап беруді ойлаймын..."
wait_msg_ua = "♻ Я думаю, що відповісти на твоє повідомлення..."
wait_msg_en = "♻ I think to answer your message..."


update_ru = "♻Обновляю..."
update_kz = "♻Жаңартамын..."
update_ua = "♻Оновлюю..."
update_en = "♻Updating..."

pay_balance_msg_ru = "💳*Пополнение баланса*\n" \
                  "Введите сумму на которую хотите пополнить ваш баланс, либо выберите из предложенных"
pay_balance_msg_kz = "💳*Балансты толтыру*\n" \
                  "Балансыңызды толтырғыңыз келетін соманы енгізіңіз немесе ұсынылғаннан таңдаңыз"
pay_balance_msg_ua = "💳*Поповнення балансу*\n" \
                  "Введіть суму, на яку хочете поповнити ваш баланс, або виберіть із запропонованих"
pay_balance_msg_en = "💳*Balance replenishment*\n" \
                  "Enter the amount you want to top up your balance, or choose from the suggested"

terms_of_use_ru = '*Пользовательское соглашение:*\n' \
               '_1. Пользователь соглашается на использование бота_ *@uai_robot* _и понимает, ' \
               'что этот бот является частью проекта "Universal Artificial Intelligence", ' \
               'который предназначен для упрощения доступа к множеству нейросетей, в рамках выбранного тарифа.\n' \
               '2. Пользователь осознает, что разработчик не имеет возможности контролировать содержание ' \
               'ответов бота, скорость и задержки.\n' \
               '3. В случае ошибок или неудовлетворительных ответов, пользователь соглашается обратиться ' \
               'к боту в другое время или сформулировать вопрос по-другому.\n' \
               '4. Пользователь соглашается использовать бота_ *@uai_robot* _только ' \
               'в законных целях и не будет использовать его для нарушения закона или прав других лиц.\n' \
               '5. Разработчик не несет ответственности за любые убытки или повреждения, ' \
               'вызванные использованием бота_ *@uai_robot.*_\n' \
               '6. Пользователь соглашается соблюдать правила использования телеграм, ' \
               'включая правила конфиденциальности и защиты персональных данных.\n' \
               '7. Разработчик оставляет за собой право изменять условия пользовательского соглашения ' \
               'в любое время без предварительного уведомления._'
terms_of_use_kz = '*Қолдану ережелері:*\n' \
               '_1. Пайдаланушы_ *@uai_robot* _ботын пайдалануға келіседі және бұл бот ' \
                  'таңдалған тариф шеңберінде әртүрлі нейрондық желілерге қолжетімділікті жеңілдетуге' \
                  ' арналған «Universal Artificial Intelligence» жобасының бөлігі екенін түсінеді.\n' \
               '2. Пайдаланушы әзірлеушінің бот жауаптарының мазмұнын, жылдамдығын және' \
                  ' кідірістерін басқару мүмкіндігі жоқ екенін мойындайды.\n' \
               '3. Қателер немесе қанағаттанарлықсыз жауаптар болған жағдайда, пайдаланушы ' \
                  'ботпен басқа уақытта байланысуға немесе сұрақты басқа жолмен тұжырымдауға келіседі.\n' \
               '4. Пайдаланушы_ *@uai_robot* _ботын тек заңды мақсаттарда пайдалануға ' \
                  'келіседі және оны заңды немесе басқалардың құқықтарын бұзу үшін пайдаланбайды.\n' \
               '5. Әзірлеуші_ *@uai_robot* _ботын пайдаланудан болған кез келген шығынға немесе зақымға жауапты емес\n' \
               '6. Пайдаланушы жеделхаттарды пайдалану ережелерін, оның ішінде ' \
                  'құпиялылық және жеке деректерді қорғау ережелерін сақтауға келіседі.\n' \
               '7. Әзірлеуші кез келген уақытта алдын ала ескертусіз пайдаланушы келісімінің ' \
                  'шарттарын өзгерту құқығын өзіне қалдырады._'
terms_of_use_ua = '*Користувача угода:*\n' \
               '_1. Користувач погоджується на використання бота_ *@uai_robot* _і розуміє, ' \
                  'що цей бот є частиною проекту "Universal Artificial Intelligence",' \
                  ' який призначений для спрощення доступу до багатьох нейромереж, в рамках обраного тарифу.\n' \
               '2. Користувач усвідомлює, що розробник немає можливості' \
                  ' контролювати зміст відповідей робота, швидкість і затримки.\n' \
               '3. У разі помилок чи незадовільних відповідей, користувач погоджується' \
                  ' звернутися до бота в інший час або сформулювати питання по-іншому.\n' \
               '4. Користувач погоджується використовувати бота_ *@uai_robot* _тільки в законних цілях і' \
                  ' не використовуватиме його для порушення закону або прав інших осіб.\n' \
               '5. Розробник не несе відповідальності за будь-які збитки або пошкодження, ' \
                  'спричинені використанням бота_ *@uai_robot.*_\n' \
               '6. Користувач погоджується дотримуватись правил використання телеграм, ' \
                  'включаючи правила конфіденційності та захисту персональних даних.\n' \
               '7. Розробник залишає за собою право змінювати умови користувальницької угоди у ' \
                  'будь-який час без попереднього повідомлення._'
terms_of_use_en = '*Terms of use:*\n' \
               '_1. The user agrees to use the bot_ *@uai_robot* _and understands that this bot is part ' \
                  'of the "Universal Artificial Intelligence" project, which is designed to simplify access to a' \
                  ' variety of neural networks, within the selected tariff.\n' \
               '2. The user acknowledges that the developer does not have the ability to control the content of the ' \
                  'bot is responses, speed and delays.\n' \
               '3. In case of errors or unsatisfactory answers, the user agrees to contact the bot at another' \
                  ' time or formulate the question in a different way.\n' \
               '4. The user agrees to use the bot_ *@uai_robot* _only for lawful purposes and will not' \
                  ' use it to violate the law or the rights of others.\n' \
               '5. The developer is not responsible for any loss or damage caused by using the bot_ *@uai_robot*_\n' \
               '6. The user agrees to comply with the rules for using telegrams, ' \
                  'including the rules of confidentiality and protection of personal data.\n' \
               '7. The developer reserves the right to change the terms of the user ' \
                  'agreement at any time without prior notice._'

welcome_message_ru = '🤖*Здравствуйте! Я искусственный интеллект, созданный быть вашим надёжным помощником. Я обладаю умением вести диалог, распознавать содержимое фотографий и даже отвечать вам голосом – выберите один из шести вариантов в меню вашего аккаунта. Чтобы начать общение, просто нажмите кнопку "🟢Начать чат".*\n\n' \
                     '⚠️ Помните, чтобы я мог корректно обработать ваше сообщение или фото, добавьте знак "!" перед ними.\n' \
                     '🔰 Например: `!Как дела?`\n' \
                     '🎙️ Также вы можете отправить голосовое сообщение, и я преобразую его в текст, сформирую ответ и вернусь к вам с ним.'
welcome_message_kz = '🤖*Сәлеметсіз бе! Мен жасанды интеллектпін, сіздің сенімді көмекшіңіз болу үшін жасалған. Мен сізбен диалог жүргізе аламын, фотосуреттердің мазмұнын тануға қабілеттімін және тіпті дауыстық жауап бере аламын – алты нұсқаның бірін сіздің аккаунт мәзірінен таңдаңыз. Әңгімелесуді бастау үшін "🟢Чатты бастау" түймесін басыңыз.*\n\n' \
                     '⚠️ Есте сақтаңыз, мен сіздің хабарламаңызды немесе фотоңызды дұрыс өңдеу үшін, олардың алдына "!" белгісін қойыңыз.\n' \
                     '🔰 Мысалы: `!Қалайсыз?`\n' \
                     '🎙️ Сондай-ақ, сіз дауыстық хабарлама жібере аласыз, мен оны мәтінге айналдырамын, жауапты қалыптастырамын және сізге онымен қайтарамын.'
welcome_message_ua = '🤖*Вітаю! Я штучний інтелект, створений бути вашим надійним помічником. Я вмію вести діалог, розпізнавати вміст фотографій та навіть відповідати вам голосом – оберіть один із шести варіантів у меню вашого акаунта. Щоб розпочати спілкування, просто натисніть кнопку "🟢Почати чат".*\n\n' \
                     '⚠️ Памятайте, щоб я міг правильно обробити ваше повідомлення або фото, додайте знак "!" перед ними.\n' \
                     '🔰 Наприклад: `!Як справи?`\n' \
                     '🎙️ Ви також можете надіслати голосове повідомлення, і я перетворю його в текст, сформую відповідь та повернуся до вас з нею.'
welcome_message_en = '🤖*Greetings! I am an artificial intelligence, designed to be your dependable assistant. I can engage in conversation with you, recognize the contents of photographs, and even respond with a voice – choose one of the six options in your account menu. To start chatting, simply press the "🟢Start Chat" button.*\n\n' \
                     '⚠️ Remember, to ensure I can properly process your message or photo, please place a "" sign before them.\n' \
                     '🔰 For example: `!How are you?`\n' \
                     '🎙️ You can also send a voice message, and I will convert it into text, formulate a response, and get back to you with it.'

image_generation_start_ru = '✍️Напишите ваш запрос(промпт) на генерацию изображения.\n' \
                            '🧑‍🎨За генерацию отвечает DALLE-3\n' \
                            '🖼️Размер изображения: 1024x1024'
image_generation_start_kz = '✍️Кескінді жасау үшін сұрауыңызды (сұрауыңызды) жазыңыз.\n' \
                            '🧑‍🎨DALLE-3 генерацияға жауапты\n' \
                            '🖼️Сурет өлшемі: 1024x1024'
image_generation_start_ua = '✍️Напишіть ваш запит(промпт) на генерацію зображення.\n' \
                            '🧑‍🎨За генерацію відповідає DALLE-3\n' \
                            '🖼️Розмір зображення: 1024x1024'
image_generation_start_en = '✍️Write your request (prompt) to generate an image.\n' \
                            '🧑‍🎨DALLE-3 is responsible for generation\n' \
                            '🖼️Image size: 1024x1024'

img_generation_ru = '🖼️Генерирую изображение...'
img_generation_kz = '🖼️Генерирую изображение...'
img_generation_ua = '🖼️Генерирую изображение...'
img_generation_en = '🖼️Генерирую изображение...'

hello_i_ai_ru = 'Привет! Я полезный помощник! Жду вашего сообщения.'
hello_i_ai_kz = 'Сәлеметсіз бе! Мен пайдалы көмекшімін! Мен сіздің хабарламаңызды күтемін.'
hello_i_ai_ua = 'Вітання! Я корисний помічник! Чекаю на ваше повідомлення.'
hello_i_ai_en = 'Hello! I am a helpful assistant! I am waiting for your message.'

error_summ_ru = '❌Пополняемая сумма должна быть целым числом, больше минимального значения!\n' \
                'Минимальные значения:\n' \
                'Россия: 10 ₽\n' \
                'Казахстан: 35 ₸\n' \
                'Украина: 35 ₴\n' \
                'Другие страны: 1 $'
error_summ_kz = '❌Толтырылған сома ең төменгі мәннен үлкен бүтін сан болуы керек!\n' \
                'Ең аз мәндер:\n' \
                'Ресей: 10 ₽\n' \
                'Қазақстан: 35 ₸\n' \
                'Украина: 35 ₴\n' \
                'Басқа елдер: 1 $'
error_summ_ua = '❌Сума, що поповнюється, повинна бути цілим числом, більше мінімального значення!\n' \
                'Мінімальні значення:\n' \
                'Росія: 10 ₽\n' \
                'Казахстан: 35 ₸\n' \
                'Україна: 35 ₴\n' \
                'Інші країни: 1 $'
error_summ_en = '❌The replenished amount must be an integer greater than the minimum value!\n' \
                'Minimum values:\n' \
                'Russia: 10 ₽\n' \
                'Kazakhstan: 35 ₸\n' \
                'Ukraine: 35 ₴\n' \
                'Other countries: 1 $'

instruction_msg_ru = '❌В нашей беседе, всегда ставьте этот'\
                     ' знак "*!*" перед вашим сообщением или фотографией, так я пойму что я должен ответить на '\
                     'сообщение, которое вы '\
                     'отправили.\n' \
                     '🔰Пример: `! Как дела?`\n' \
                     '🎤Либо вы можете отправить голосовое сообщение с вашим вопросом, а я его расшифрую, сгенерирую ответ и отвечу вам! '
instruction_msg_kz = '❌ Біздің әңгімемізде, әрдайым осы белгіні "*!*" хабарламаңызға немесе фотосуретіңізге қойыңыз, сонда мен сіз жіберген хабарламаға жауап беруім керек екенін түсінемін.\n' \
                     '🔰 Мысалы: `!Қалайсыз?`\n' \
                     '🎤 Немесе сіз өз сұрағыңызбен дауыстық хабарлама жібере аласыз, мен оны түсіндіріп, жауап жасап, сізге жауап беремін.'
instruction_msg_ua = '❌ У нашій розмові завжди ставте цей знак "*!*" перед вашим повідомленням або фотографією, так я зрозумію, що я повинен відповісти на повідомлення, яке ви надіслали.\n' \
                     '🔰 Приклад: `!Як справи?`\n' \
                     '🎤 Або ви можете надіслати голосове повідомлення з вашим запитанням, а я його розшифрую, сгенерую відповідь і відповім вам.'
instruction_msg_en = '❌ In our conversation, always place this sign "*!*" before your message or photograph, so I understand that I need to respond to the message you sent.\n' \
                     '🔰 Example: `!How are you?`\n' \
                     '🎤 Or you can send a voice message with your question, and I will decipher it, generate a response, and reply to you.'

success_country_changed_ru = '✅Страна успешно изменена!'
success_country_changed_kz = '✅Ел сәтті өзгертілді!'
success_country_changed_ua = '✅Країна успішно змінена!'
success_country_changed_en = '✅The country has been successfully changed!'

success_ai_model_changed_ru = '✅Смена нейросети успешно выполнена!'
success_ai_model_changed_kz = '✅Нейрондық желі сәтті өзгертілді!'
success_ai_model_changed_ua = '✅Зміна нейромережі успішно виконана!'
success_ai_model_changed_en = '✅The neural network has been changed successfully!'

success_ai_voice_changed_ru = '✅Смена голоса нейросети успешно выполнена!'
success_ai_voice_changed_kz = '✅Нейрондық желінің дауысын өзгерту сәтті аяқталды!'
success_ai_voice_changed_ua = '✅Зміна голосу нейромережі успішно виконана!'
success_ai_voice_changed_en = '✅Changing the voice of the neural network has been successfully completed!'

choose_lanuage_text = 'ℹВыберите язык интерфейса бота:\n' \
                      'ℹБот интерфейсінің тілін таңдаңыз:\n' \
                      'ℹВиберіть мову інтерфейсу бота:\n' \
                      'ℹSelect the language of the bot interface:'
change_lanuage_text = 'ℹВыберите язык интерфейса бота:\n' \
                      'ℹБот интерфейсінің тілін таңдаңыз:\n' \
                      'ℹВиберіть мову інтерфейсу бота:\n' \
                      'ℹSelect the language of the bot interface:'
choose_country_text = 'ℹВыберите страну проживания:\n' \
                      'ℹТұратын елді таңдаңыз:\n' \
                      'ℹВиберіть країну проживання:\n' \
                      'ℹSelect country of residence:'
change_country_text = 'ℹВыберите страну проживания:\n' \
                      'ℹТұратын елді таңдаңыз:\n' \
                      'ℹВиберіть країну проживання:\n' \
                      'ℹSelect country of residence:'