import json
import os
import random
import threading
import time
import openai
import psycopg2 as psycopg2
import requests
import telebot
from telebot import types
import datetime
from config import *
from flask import Flask, request, abort
import decimal
import hashlib
import subprocess
from yookassa import Configuration, Payment
import uuid
import tiktoken
from mutagen.mp3 import MP3
import schedule
import base64

Configuration.account_id = account_id
Configuration.secret_key = secret_key

bot = telebot.TeleBot(API_TOKEN)

app = Flask(__name__)

choose_lanuage = types.InlineKeyboardMarkup(row_width=1)
change_language = types.InlineKeyboardMarkup(row_width=1)
choose_country = types.InlineKeyboardMarkup(row_width=1)
change_country = types.InlineKeyboardMarkup(row_width=1)
admin_menu = types.InlineKeyboardMarkup(row_width=1)
admin_back = types.InlineKeyboardMarkup(row_width=1)

russian_language = types.InlineKeyboardButton(text="Русский язык", callback_data='russian_language')
kazakh_language = types.InlineKeyboardButton(text="Қазақ тілі", callback_data='kazakh_language')
ukrain_language = types.InlineKeyboardButton(text="Українська мова", callback_data='ukrain_language')
english_language = types.InlineKeyboardButton(text="English language", callback_data='english_language')
russian_language_change = types.InlineKeyboardButton(text="Русский язык", callback_data='russian_language_change')
kazakh_language_change = types.InlineKeyboardButton(text="Қазақ тілі", callback_data='kazakh_language_change')
ukrain_language_change = types.InlineKeyboardButton(text="Українська мова", callback_data='ukrain_language_change')
english_language_change = types.InlineKeyboardButton(text="English language", callback_data='english_language_change')
russian_country = types.InlineKeyboardButton(text="🇷🇺Россия ₽", callback_data='russian_country')
kazakh_country = types.InlineKeyboardButton(text="🇰🇿Казахстан ₸", callback_data='kazakh_country')
ukrain_country = types.InlineKeyboardButton(text="🇺🇦Україна ₴", callback_data='ukrain_country')
other_country = types.InlineKeyboardButton(text="Other country $", callback_data='other_country')
russian_country_change = types.InlineKeyboardButton(text="🇷🇺Россия ₽", callback_data='russian_country_change')
kazakh_country_change = types.InlineKeyboardButton(text="🇰🇿Казахстан ₸", callback_data='kazakh_country_change')
ukrain_country_change = types.InlineKeyboardButton(text="🇺🇦Україна ₴", callback_data='ukrain_country_change')
other_country_change = types.InlineKeyboardButton(text="Other country $", callback_data='other_country_change')

update_admin = types.InlineKeyboardButton(text="Обновить меню", callback_data='update_admin')
off_on_button = types.InlineKeyboardButton(text="Статус бота", callback_data='status_bot')
token_button = types.InlineKeyboardButton(text="Количество токенов на сообщение", callback_data='token_message')
temperature_button = types.InlineKeyboardButton(text="Температура на сообщение", callback_data='temperature_message')
add_balance_button = types.InlineKeyboardButton(text="Пополнить баланс пользователя", callback_data='add_balance')
bonus_referal_button = types.InlineKeyboardButton(text="Бонусы реферала", callback_data='bonus_referal')
bonus_reffer_button = types.InlineKeyboardButton(text="Бонусы рефера", callback_data='bonus_reffer')
trial_bonus_button = types.InlineKeyboardButton(text="Триал бонус для новых пользователей", callback_data='trial_bonus')
GPT4_price_button = types.InlineKeyboardButton(text="GPT-4 прайс", callback_data='gpt-4_price')
GPT3_price_button = types.InlineKeyboardButton(text="GPT-3.5-turbo прайс", callback_data='gpt-3_price')
Whisper_price_button = types.InlineKeyboardButton(text="Whisper прайс", callback_data='whisper_price')
cashback_button = types.InlineKeyboardButton(text="Кешбек для пользователей", callback_data='cashback_button')
free_api_button = types.InlineKeyboardButton(text="Бесплатный API", callback_data='free_api_button')
all_message_button = types.InlineKeyboardButton(text="Рассылка", callback_data='all_message')
back_admin_button = types.InlineKeyboardButton(text="Вернуться в меню", callback_data='back_admin')

choose_lanuage.add(russian_language, kazakh_language, ukrain_language, english_language)
change_language.add(russian_language_change, kazakh_language_change, ukrain_language_change, english_language_change)
choose_country.add(russian_country, kazakh_country, ukrain_country, other_country)
change_country.add(russian_country_change, kazakh_country_change, ukrain_country_change, other_country_change)

admin_menu.add(update_admin, off_on_button, token_button, temperature_button, add_balance_button, bonus_reffer_button,
               bonus_referal_button, trial_bonus_button, GPT4_price_button, GPT3_price_button, Whisper_price_button,
               cashback_button, free_api_button, all_message_button)
admin_back.add(back_admin_button)


# Локализация интерфейса под разные языки
def get_interface(user_id, interface):
    terms_markup = types.InlineKeyboardMarkup(row_width=1)
    welcome = types.InlineKeyboardMarkup(row_width=1)
    user_menu = types.InlineKeyboardMarkup(row_width=1)
    user_back = types.InlineKeyboardMarkup(row_width=1)
    chat_settings = types.InlineKeyboardMarkup(row_width=1)
    close_msg = types.InlineKeyboardMarkup(row_width=1)
    change_ai_model_markup = types.InlineKeyboardMarkup(row_width=2)
    GPT4_change_button = types.InlineKeyboardButton(text="🧠GPT-4-TURBO", callback_data='change_gpt4')
    GPT3_change_button = types.InlineKeyboardButton(text="🚀GPT-3.5-TURBO", callback_data='change_gpt3')
    change_ai_model_markup.add(GPT4_change_button, GPT3_change_button)
    db_results = db_all_get(f"SELECT * FROM users WHERE user_id = {user_id}")
    language = db_results[10]
    country = db_results[11]
    if language == "Русский":
        if interface == 'terms_markup':
            yes_terms = types.InlineKeyboardButton(text="✅Принимаю", callback_data='yes_terms')
            terms_markup.add(yes_terms)
            return terms_markup
        if interface == 'welcome':
            menu_button = types.InlineKeyboardButton(text="👤Аккаунт", callback_data='menu_button')
            start_chat = types.InlineKeyboardButton(text="🟢Начать чат", callback_data='start_chat')
            start_image = types.InlineKeyboardButton(text="🖼️Сгенерировать изображение",
                                                     callback_data='image_generation')
            welcome.add(menu_button, start_chat, start_image)
            return welcome
        if interface == 'user_menu':
            update_user = types.InlineKeyboardButton(text="🔁Обновить меню", callback_data='update_user')
            add_balance_button = types.InlineKeyboardButton(text="💳Пополнить баланс", callback_data='buy_balance')
            my_transactions = types.InlineKeyboardButton(text='🧾Мои операции', callback_data='my_transactions')
            change_ai_model = types.InlineKeyboardButton(text='🤖Изменить модель ИИ', callback_data='change_ai_model')
            change_voice_model = types.InlineKeyboardButton(text='🔊Изменить голос ИИ', callback_data='change_ai_voice')
            my_chats = types.InlineKeyboardButton(text="💬Мои чаты", callback_data='chats_menu')
            change_country = types.InlineKeyboardButton(text='🌐Изменить страну',
                                                        callback_data='change_country')
            change_language = types.InlineKeyboardButton(text='🗣Изменить язык интерфейса',
                                                         callback_data='change_language')
            price_button = types.InlineKeyboardButton(text="ℹ️Наши цены", callback_data='price_info')
            support_button = types.InlineKeyboardButton(text="🆘Поддержка", url=url_support)
            user_welcome_button = types.InlineKeyboardButton(text="↩Назад", callback_data='welcome_menu')
            user_menu.add(update_user, add_balance_button, change_ai_model, change_voice_model, my_transactions,
                          my_chats, change_country,
                          change_language, price_button, support_button,
                          user_welcome_button)
            return user_menu
        if interface == 'change_voice_model_menu_ru':
            voice_model_menu = types.InlineKeyboardMarkup(row_width=1)
            voice1 = types.InlineKeyboardButton(text='🙍‍♀️Алиса', callback_data='voice1')
            voice2 = types.InlineKeyboardButton(text='👨Андрей', callback_data='voice2')
            voice3 = types.InlineKeyboardButton(text='👨‍🦲Дмитрий', callback_data='voice3')
            voice4 = types.InlineKeyboardButton(text='👨‍🦱Тимофей', callback_data='voice4')
            voice5 = types.InlineKeyboardButton(text='👩Вероника', callback_data='voice5')
            voice6 = types.InlineKeyboardButton(text='👩‍🦱Анастасия', callback_data='voice6')
            user_back_button = types.InlineKeyboardButton(text="↩Вернуться в меню",
                                                          callback_data='back_user_from_voice')
            voice_model_menu.add(voice1, voice2, voice3, voice4, voice5, voice6, user_back_button)
            return voice_model_menu
        if interface == 'user_back':
            user_back_button = types.InlineKeyboardButton(text="↩Вернуться в меню", callback_data='back_user')
            user_back.add(user_back_button)
            return user_back
        if interface == 'close_msg':
            close_msg_button = types.InlineKeyboardButton(text="❌Закрыть", callback_data='close_msg')
            close_msg.add(close_msg_button)
            return close_msg
        if interface == 'chat_settings':
            if db_results[14]:
                voice_button = types.InlineKeyboardButton(text='🔇Выключить озвучивание ответов',
                                                          callback_data='voice_off')
            else:
                voice_button = types.InlineKeyboardButton(text='🔈Включить озвучивание ответов',
                                                          callback_data='voice_on')
            end_chat = types.InlineKeyboardButton(text="🔴Завершить чат", callback_data='end_chat')
            chat_settings.add(voice_button, end_chat)
            return chat_settings
        if interface == 'chats_menu':
            chats_menu = types.InlineKeyboardMarkup(row_width=1)
            all_msgs = types.InlineKeyboardButton(text='💬Получить все чаты', callback_data='get_all_chats')
            get_chat = types.InlineKeyboardButton(text='🗨️Получить определенный чат', callback_data='get_one_chat')
            delete_history = types.InlineKeyboardButton(text='🗑️Удалить историю сообщений',
                                                        callback_data='delete_history')
            user_back_button = types.InlineKeyboardButton(text="↩Вернуться в меню",
                                                          callback_data='back_user')
            chats_menu.add(all_msgs, get_chat, delete_history, user_back_button)
            return chats_menu
        if interface == 'chats_menu_text':
            return chats_menu_text_ru
        if interface == 'input_chat_number':
            return chat_input_text_ru
        if interface == 'your_chat_one_text':
            return your_chat_one_ru
        if interface == 'error_get_chat':
            return error_get_chat_text_ru
        if interface == 'delete_history_complete':
            return delete_history_complete_ru
        if interface == 'price_info':
            return price_ru
        if interface == 'image_generation_start':
            return image_generation_start_ru
        if interface == 'img_generation':
            return img_generation_ru
        if interface == 'terms_text':
            return terms_of_use_ru
        if interface == 'welcome_text':
            return welcome_message_ru
        if interface == 'pay_balance_text':
            return pay_balance_msg_ru
        if interface == 'update_text':
            return update_ru
        if interface == 'error_text':
            return error_openai_ru
        if interface == 'error_unknow_text':
            return error_unkown_ru
        if interface == 'error_unknow2_text':
            return error_unkown2_ru
        if interface == 'error_text_msg':
            return error_text_msg_ru
        if interface == 'error_delete_msg':
            return error_delete_msg_ru
        if interface == 'bot_out':
            return bot_out_ru
        if interface == 'wait_msg':
            return wait_msg_ru
        if interface == 'end_chat_text':
            return chat_end_text_ru
        if interface == 'your_chat_text':
            return your_chat_ru
        if interface == 'your_chats_text':
            return your_chats_ru
        if interface == 'error_create_chat':
            return error_create_chat_ru
        if interface == 'welcome_chat_text':
            return hello_i_ai_ru
        if interface == 'instruction_text':
            return instruction_msg_ru
        if interface == 'error_summ':
            return error_summ_ru
        if interface == 'success_changed_country':
            return success_country_changed_ru
        if interface == 'success_ai_voice_changed':
            return success_ai_voice_changed_ru
        if interface == 'russia_country':
            return "Россия"
        if interface == 'kazakhstan_country':
            return "Казахстан"
        if interface == 'ukraina_country':
            return "Украина"
        if interface == 'other_country':
            return "???"
        if interface == 'your_transactions_text':
            return your_transactions_ru
        if interface == "insufficient_funds":
            return error_money_ru
        if interface == 'subscribe_invite':
            return subscribe_invite_ru
        if interface == 'subscribe_menu':
            menu = types.InlineKeyboardMarkup(row_width=1)
            subscribe_button = types.InlineKeyboardButton(text='💎Подписаться!', url=url_channel)
            subscribed_button = types.InlineKeyboardButton(text='✅Подписался!', callback_data='subscribed')
            menu.add(subscribe_button, subscribed_button)
            return menu
        if interface == 'subscribe_warning':
            menu = types.InlineKeyboardMarkup(row_width=1)
            subscribe_button = types.InlineKeyboardButton(text='💎Подписаться!', url=url_channel)
            close_msg_button = types.InlineKeyboardButton(text="❌Закрыть!", callback_data='close_msg')
            menu.add(subscribe_button, close_msg_button)
            return menu
        if interface == 'error_openai_load':
            return error_openai_load_ru
        if interface == 'pay_desc':
            return pay_desc_ru
        if interface == 'empty_voice':
            return voice_empty_ru
        if interface == 'voice_message':
            return voice_message_ru
        if interface == 'recognize_voice':
            return recognize_voice_ru
        if interface == 'rashod':
            if country == "Россия":
                return rashod_ru.format("₽", "₽", "₽", "₽", "₽")
            elif country == "Казахстан":
                return rashod_ru.format("₸", "₸", "₸", "₸", "₸")
            elif country == "Украина":
                return rashod_ru.format("₴", "₴", "₴", "₴", "₴")
            else:
                return rashod_ru.format("$", "$", "$", "$", "$")
        if interface == 'change_ai_model_text':
            return change_ai_model_ru
        if interface == 'change_ai_model_markup':
            user_back_button = types.InlineKeyboardButton(text="↩Вернуться в меню", callback_data='back_user')
            change_ai_model_markup.row_width = 1
            change_ai_model_markup.add(user_back_button)
            return change_ai_model_markup
        if interface == 'success_changed_ai_model':
            return success_ai_model_changed_ru
        if interface == 'process_transactions':
            return process_file_operation_ru
        if interface == 'process_chats':
            return process_file_chats_ru
        if interface == 'photo_gpt':
            return use_gpt4_ru
    if language == "Казахский":
        if interface == 'terms_markup':
            yes_terms = types.InlineKeyboardButton(text="✅Қабылдау", callback_data='yes_terms')
            terms_markup.add(yes_terms)
            return terms_markup
        if interface == 'welcome':
            menu_button = types.InlineKeyboardButton(text="👤Аккаунт", callback_data='menu_button')
            start_chat = types.InlineKeyboardButton(text="🟢Чатты бастау", callback_data='start_chat')
            start_image = types.InlineKeyboardButton(text="🖼️Кескінді жасау",
                                                     callback_data='image_generation')
            welcome.add(menu_button, start_chat, start_image)
            return welcome
        if interface == 'user_menu':
            update_user = types.InlineKeyboardButton(text="🔁Жаңарту мәзірі", callback_data='update_user')
            add_balance_button = types.InlineKeyboardButton(text="💳Балансты толтыру", callback_data='buy_balance')
            change_ai_model = types.InlineKeyboardButton(text='🤖AI үлгісін өзгерту',
                                                         callback_data='change_ai_model')
            change_voice_model = types.InlineKeyboardButton(text='🔊AI дауысын өзгертіңіз',
                                                            callback_data='change_ai_voice')
            my_transactions = types.InlineKeyboardButton(text='🧾Менің транзакциялар', callback_data='my_transactions')
            my_chats = types.InlineKeyboardButton(text="💬Менің чаттар", callback_data='chats_menu')
            change_country = types.InlineKeyboardButton(text='🌐Елді өзгерту',
                                                        callback_data='change_country')
            change_language = types.InlineKeyboardButton(text='🗣Интерфейс тілін өзгерту',
                                                         callback_data='change_language')
            price_button = types.InlineKeyboardButton(text="ℹ️Біздің бағалар", callback_data='price_info')
            support_button = types.InlineKeyboardButton(text="🆘Қолдау қызметі", url=url_support)
            user_welcome_button = types.InlineKeyboardButton(text="↩Артқа", callback_data='welcome_menu')
            user_menu.add(update_user, add_balance_button, change_ai_model, change_voice_model, my_transactions,
                          my_chats, change_country,
                          change_language, price_button, support_button,
                          user_welcome_button)
            return user_menu
        if interface == 'change_voice_model_menu_kz':
            voice_model_menu = types.InlineKeyboardMarkup(row_width=1)
            voice1 = types.InlineKeyboardButton(text='🙍‍♀️Адель', callback_data='voice1')
            voice2 = types.InlineKeyboardButton(text='👨Айдар', callback_data='voice2')
            voice3 = types.InlineKeyboardButton(text='👨‍🦲Дамир', callback_data='voice3')
            voice4 = types.InlineKeyboardButton(text='👨‍🦱Тамерлан', callback_data='voice4')
            voice5 = types.InlineKeyboardButton(text='👩Асель', callback_data='voice5')
            voice6 = types.InlineKeyboardButton(text='👩‍🦱Әлия', callback_data='voice6')
            user_back_button = types.InlineKeyboardButton(text="↩Мәзірге оралу", callback_data='back_user_from_voice')
            voice_model_menu.add(voice1, voice2, voice3, voice4, voice5, voice6, user_back_button)
            return voice_model_menu
        if interface == 'user_back':
            user_back_button = types.InlineKeyboardButton(text="↩Мәзірге оралу", callback_data='back_user')
            user_back.add(user_back_button)
            return user_back
        if interface == 'close_msg':
            close_msg_button = types.InlineKeyboardButton(text="❌Жабық", callback_data='close_msg')
            close_msg.add(close_msg_button)
            return close_msg
        if interface == 'chat_settings':
            if db_results[14]:
                voice_button = types.InlineKeyboardButton(text='🔇Дауыстық жауаптарды өшіріңіз',
                                                          callback_data='voice_off')
            else:
                voice_button = types.InlineKeyboardButton(text='🔈Дауыстық жауаптарды қосыңыз', callback_data='voice_on')
            end_chat = types.InlineKeyboardButton(text="🔴Чатты аяқтау", callback_data='end_chat')
            chat_settings.add(voice_button, end_chat)
            return chat_settings
        if interface == 'chats_menu':
            chats_menu = types.InlineKeyboardMarkup(row_width=1)
            all_msgs = types.InlineKeyboardButton(text='💬Барлық чаттарды алыңыз', callback_data='get_all_chats')
            get_chat = types.InlineKeyboardButton(text='🗨️Арнайы чатты алыңыз', callback_data='get_one_chat')
            delete_history = types.InlineKeyboardButton(text='🗑️Хабарлама тарихын жою', callback_data='delete_history')
            user_back_button = types.InlineKeyboardButton(text="↩Мәзірге оралу", callback_data='back_user')
            chats_menu.add(all_msgs, get_chat, delete_history, user_back_button)
            return chats_menu
        if interface == 'chats_menu_text':
            return chats_menu_text_kz
        if interface == 'input_chat_number':
            return chat_input_text_kz
        if interface == 'your_chat_one_text':
            return your_chat_one_kz
        if interface == 'error_get_chat':
            return error_get_chat_text_kz
        if interface == 'delete_history_complete':
            return delete_history_complete_kz
        if interface == 'price_info':
            return price_kz
        if interface == 'image_generation_start':
            return image_generation_start_kz
        if interface == 'img_generation':
            return img_generation_kz
        if interface == 'terms_text':
            return terms_of_use_kz
        if interface == 'welcome_text':
            return welcome_message_kz
        if interface == 'pay_balance_text':
            return pay_balance_msg_kz
        if interface == 'update_text':
            return update_kz
        if interface == 'error_text':
            return error_openai_kz
        if interface == 'error_unknow_text':
            return error_unkown_kz
        if interface == 'error_unknow2_text':
            return error_unkown2_kz
        if interface == 'error_text_msg':
            return error_text_msg_kz
        if interface == 'error_delete_msg':
            return error_delete_msg_kz
        if interface == 'bot_out':
            return bot_out_kz
        if interface == 'wait_msg':
            return wait_msg_kz
        if interface == 'end_chat_text':
            return chat_end_text_kz
        if interface == 'your_chat_text':
            return your_chat_kz
        if interface == 'your_chats_text':
            return your_chats_kz
        if interface == 'error_create_chat':
            return error_create_chat_kz
        if interface == 'welcome_chat_text':
            return hello_i_ai_kz
        if interface == 'instruction_text':
            return instruction_msg_kz
        if interface == 'error_summ':
            return error_summ_kz
        if interface == 'success_changed_country':
            return success_country_changed_kz
        if interface == 'success_ai_voice_changed':
            return success_ai_voice_changed_kz
        if interface == 'russia_country':
            return "Ресей"
        if interface == 'kazakhstan_country':
            return "Қазақстан"
        if interface == 'ukraina_country':
            return "Украина"
        if interface == 'other_country':
            return "???"
        if interface == 'your_transactions_text':
            return your_transactions_kz
        if interface == "insufficient_funds":
            return error_money_kz
        if interface == 'subscribe_invite':
            return subscribe_invite_kz
        if interface == 'subscribe_menu':
            menu = types.InlineKeyboardMarkup(row_width=1)
            subscribe_button = types.InlineKeyboardButton(text='💎Белгісі!', url=url_channel)
            subscribed_button = types.InlineKeyboardButton(text='✅Жазылды!', callback_data='subscribed')
            menu.add(subscribe_button, subscribed_button)
            return menu
        if interface == 'subscribe_warning':
            menu = types.InlineKeyboardMarkup(row_width=1)
            subscribe_button = types.InlineKeyboardButton(text='💎Белгісі!', url=url_channel)
            close_msg_button = types.InlineKeyboardButton(text="❌Жабық", callback_data='close_msg')
            menu.add(subscribe_button, close_msg_button)
            return menu
        if interface == 'error_openai_load':
            return error_openai_load_kz
        if interface == 'pay_desc':
            return pay_desc_kz
        if interface == 'empty_voice':
            return voice_empty_kz
        if interface == 'voice_message':
            return voice_message_kz
        if interface == 'recognize_voice':
            return recognize_voice_kz
        if interface == 'rashod':
            if country == "Россия":
                return rashod_kz.format("₽", "₽", "₽", "₽", "₽")
            elif country == "Казахстан":
                return rashod_kz.format("₸", "₸", "₸", "₸", "₸")
            elif country == "Украина":
                return rashod_kz.format("₴", "₴", "₴", "₴", "₴")
            else:
                return rashod_kz.format("$", "$", "$", "$", "$")
        if interface == 'change_ai_model_text':
            return change_ai_model_kz
        if interface == 'change_ai_model_markup':
            user_back_button = types.InlineKeyboardButton(text="↩Мәзірге оралу", callback_data='back_user')
            change_ai_model_markup.row_width = 1
            change_ai_model_markup.add(user_back_button)
            return change_ai_model_markup
        if interface == 'success_changed_ai_model':
            return success_ai_model_changed_kz
        if interface == 'process_transactions':
            return process_file_operation_kz
        if interface == 'process_chats':
            return process_file_chats_kz
        if interface == 'photo_gpt':
            return use_gpt4_kz
    if language == "Украинский":
        if interface == 'terms_markup':
            yes_terms = types.InlineKeyboardButton(text="✅Приймаю", callback_data='yes_terms')
            terms_markup.add(yes_terms)
            return terms_markup
        if interface == 'welcome':
            menu_button = types.InlineKeyboardButton(text="👤Акаунт", callback_data='menu_button')
            start_chat = types.InlineKeyboardButton(text="🟢Почати чат", callback_data='start_chat')
            start_image = types.InlineKeyboardButton(text="🖼️Згенерувати зображення",
                                                     callback_data='image_generation')
            welcome.add(menu_button, start_chat, start_image)
            return welcome
        if interface == 'user_menu':
            update_user = types.InlineKeyboardButton(text="🔁Оновити меню", callback_data='update_user')
            add_balance_button = types.InlineKeyboardButton(text="💳Поповнити баланс", callback_data='buy_balance')
            change_ai_model = types.InlineKeyboardButton(text='🤖Змінити модель ІІ',
                                                         callback_data='change_ai_model')
            change_voice_model = types.InlineKeyboardButton(text='🔊Змінити голос ІІ',
                                                            callback_data='change_ai_voice')
            my_transactions = types.InlineKeyboardButton(text='🧾Мої операції', callback_data='my_transactions')
            my_chats = types.InlineKeyboardButton(text="💬Мої чати", callback_data='chats_menu')
            change_country = types.InlineKeyboardButton(text='🌐Змінити країну',
                                                        callback_data='change_country')
            change_language = types.InlineKeyboardButton(text='🗣Змінити мову інтерфейсу',
                                                         callback_data='change_language')
            price_button = types.InlineKeyboardButton(text="ℹ️Наші ціни", callback_data='price_info')
            support_button = types.InlineKeyboardButton(text="🆘Підтримка", url=url_support)
            user_welcome_button = types.InlineKeyboardButton(text="↩Назад", callback_data='welcome_menu')
            user_menu.add(update_user, add_balance_button, change_ai_model, change_voice_model, my_transactions,
                          my_chats, change_country,
                          change_language, price_button, support_button,
                          user_welcome_button)
            return user_menu
        if interface == 'change_voice_model_menu_ua':
            voice_model_menu = types.InlineKeyboardMarkup(row_width=1)
            voice1 = types.InlineKeyboardButton(text='🙍‍♀️Аліса', callback_data='voice1')
            voice2 = types.InlineKeyboardButton(text='👨Андрій', callback_data='voice2')
            voice3 = types.InlineKeyboardButton(text='👨‍🦲Дмитро', callback_data='voice3')
            voice4 = types.InlineKeyboardButton(text='👨‍🦱Тимофій', callback_data='voice4')
            voice5 = types.InlineKeyboardButton(text='👩Вероніка', callback_data='voice5')
            voice6 = types.InlineKeyboardButton(text='👩‍🦱Анастасія', callback_data='voice6')
            user_back_button = types.InlineKeyboardButton(text="↩Повернутись до меню",
                                                          callback_data='back_user_from_voice')
            voice_model_menu.add(voice1, voice2, voice3, voice4, voice5, voice6, user_back_button)
            return voice_model_menu
        if interface == 'user_back':
            user_back_button = types.InlineKeyboardButton(text="↩Повернутись до меню", callback_data='back_user')
            user_back.add(user_back_button)
            return user_back
        if interface == 'close_msg':
            close_msg_button = types.InlineKeyboardButton(text="❌Закрити", callback_data='close_msg')
            close_msg.add(close_msg_button)
            return close_msg
        if interface == 'chat_settings':
            if db_results[14]:
                voice_button = types.InlineKeyboardButton(text='🔇Вимкнути озвучування відповідей',
                                                          callback_data='voice_off')
            else:
                voice_button = types.InlineKeyboardButton(text='🔈Включити озвучування відповідей',
                                                          callback_data='voice_on')
            end_chat = types.InlineKeyboardButton(text="🔴Завершити чат", callback_data='end_chat')
            chat_settings.add(voice_button, end_chat)
            return chat_settings
        if interface == 'chats_menu':
            chats_menu = types.InlineKeyboardMarkup(row_width=1)
            all_msgs = types.InlineKeyboardButton(text='💬Отримати всі чати', callback_data='get_all_chats')
            get_chat = types.InlineKeyboardButton(text='🗨️Отримати певний чат', callback_data='get_one_chat')
            delete_history = types.InlineKeyboardButton(text='🗑️Видалити історію повідомлень',
                                                        callback_data='delete_history')
            user_back_button = types.InlineKeyboardButton(text="↩Повернутись до меню",
                                                          callback_data='back_user')
            chats_menu.add(all_msgs, get_chat, delete_history, user_back_button)
            return chats_menu
        if interface == 'chats_menu_text':
            return chats_menu_text_ua
        if interface == 'input_chat_number':
            return chat_input_text_ua
        if interface == 'your_chat_one_text':
            return your_chat_one_ua
        if interface == 'error_get_chat':
            return error_get_chat_text_ua
        if interface == 'delete_history_complete':
            return delete_history_complete_ua
        if interface == 'price_info':
            return price_ua
        if interface == 'image_generation_start':
            return image_generation_start_ua
        if interface == 'img_generation':
            return img_generation_ua
        if interface == 'terms_text':
            return terms_of_use_ua
        if interface == 'welcome_text':
            return welcome_message_ua
        if interface == 'pay_balance_text':
            return pay_balance_msg_ua
        if interface == 'update_text':
            return update_ua
        if interface == 'error_text':
            return error_openai_ua
        if interface == 'error_unknow_text':
            return error_unkown_ua
        if interface == 'error_unknow2_text':
            return error_unkown2_ua
        if interface == 'error_text_msg':
            return error_text_msg_ua
        if interface == 'error_delete_msg':
            return error_delete_msg_ua
        if interface == 'bot_out':
            return bot_out_ua
        if interface == 'wait_msg':
            return wait_msg_ua
        if interface == 'end_chat_text':
            return chat_end_text_ua
        if interface == 'your_chat_text':
            return your_chat_ua
        if interface == 'your_chats_text':
            return your_chats_ua
        if interface == 'error_create_chat':
            return error_create_chat_ua
        if interface == 'welcome_chat_text':
            return hello_i_ai_ua
        if interface == 'instruction_text':
            return instruction_msg_ua
        if interface == 'error_summ':
            return error_summ_ua
        if interface == 'success_changed_country':
            return success_country_changed_ua
        if interface == 'success_ai_voice_changed':
            return success_ai_voice_changed_ua
        if interface == 'russia_country':
            return "Росія"
        if interface == 'kazakhstan_country':
            return "Казахстан"
        if interface == 'ukraina_country':
            return "Україна"
        if interface == 'other_country':
            return "???"
        if interface == 'your_transactions_text':
            return your_transactions_ua
        if interface == "insufficient_funds":
            return error_money_ua
        if interface == 'subscribe_invite':
            return subscribe_invite_ua
        if interface == 'subscribe_menu':
            menu = types.InlineKeyboardMarkup(row_width=1)
            subscribe_button = types.InlineKeyboardButton(text='💎Підписатись!', url=url_channel)
            subscribed_button = types.InlineKeyboardButton(text='✅Підписався!', callback_data='subscribed')
            menu.add(subscribe_button, subscribed_button)
            return menu
        if interface == 'subscribe_warning':
            menu = types.InlineKeyboardMarkup(row_width=1)
            subscribe_button = types.InlineKeyboardButton(text='💎Підписатись!', url=url_channel)
            close_msg_button = types.InlineKeyboardButton(text="❌Закрити", callback_data='close_msg')
            menu.add(subscribe_button, close_msg_button)
            return menu
        if interface == 'error_openai_load':
            return error_openai_load_ua
        if interface == 'pay_desc':
            return pay_desc_ua
        if interface == 'empty_voice':
            return voice_empty_ua
        if interface == 'voice_message':
            return voice_message_ua
        if interface == 'recognize_voice':
            return recognize_voice_ua
        if interface == 'rashod':
            if country == "Россия":
                return rashod_ua.format("₽", "₽", "₽", "₽", "₽")
            elif country == "Казахстан":
                return rashod_ua.format("₸", "₸", "₸", "₸", "₸")
            elif country == "Украина":
                return rashod_ua.format("₴", "₴", "₴", "₴", "₴")
            else:
                return rashod_ua.format("$", "$", "$", "$", "$")
        if interface == 'change_ai_model_text':
            return change_ai_model_ua
        if interface == 'change_ai_model_markup':
            user_back_button = types.InlineKeyboardButton(text="↩Повернутись до меню", callback_data='back_user')
            change_ai_model_markup.row_width = 1
            change_ai_model_markup.add(user_back_button)
            return change_ai_model_markup
        if interface == 'success_changed_ai_model':
            return success_ai_model_changed_ua
        if interface == 'process_transactions':
            return process_file_operation_ua
        if interface == 'process_chats':
            return process_file_chats_ua
        if interface == 'photo_gpt':
            return use_gpt4_ua
    if language == "Английский":
        if interface == 'terms_markup':
            yes_terms = types.InlineKeyboardButton(text="✅I accept", callback_data='yes_terms')
            terms_markup.add(yes_terms)
            return terms_markup
        if interface == 'welcome':
            menu_button = types.InlineKeyboardButton(text="👤Account", callback_data='menu_button')
            start_chat = types.InlineKeyboardButton(text="🟢Start chat", callback_data='start_chat')
            start_image = types.InlineKeyboardButton(text="🖼️Generate image",
                                                     callback_data='image_generation')
            welcome.add(menu_button, start_chat, start_image)
            return welcome
        if interface == 'user_menu':
            update_user = types.InlineKeyboardButton(text="🔁Update Menu", callback_data='update_user')
            add_balance_button = types.InlineKeyboardButton(text="💳Top up balance", callback_data='buy_balance')
            change_ai_model = types.InlineKeyboardButton(text='🤖Change AI model',
                                                         callback_data='change_ai_model')
            change_voice_model = types.InlineKeyboardButton(text='🔊Change AI voice',
                                                            callback_data='change_ai_voice')
            my_transactions = types.InlineKeyboardButton(text='🧾My transactions', callback_data='my_transactions')
            my_chats = types.InlineKeyboardButton(text="💬My chats", callback_data='chats_menu')
            change_country = types.InlineKeyboardButton(text='🌐Change the country',
                                                        callback_data='change_country')
            change_language = types.InlineKeyboardButton(text='🗣Change interface language',
                                                         callback_data='change_language')
            price_button = types.InlineKeyboardButton(text="ℹ️Our prices", callback_data='price_info')
            support_button = types.InlineKeyboardButton(text="🆘Support", url=url_support)
            user_welcome_button = types.InlineKeyboardButton(text="↩Back", callback_data='welcome_menu')
            user_menu.add(update_user, add_balance_button, change_ai_model, change_voice_model, my_transactions,
                          my_chats, change_country,
                          change_language, price_button, support_button,
                          user_welcome_button)
            return user_menu
        if interface == 'change_voice_model_menu_en':
            voice_model_menu = types.InlineKeyboardMarkup(row_width=1)
            voice1 = types.InlineKeyboardButton(text='🙍‍♀️Alloy', callback_data='voice1')
            voice2 = types.InlineKeyboardButton(text='👨Echo', callback_data='voice2')
            voice3 = types.InlineKeyboardButton(text='👨‍🦲Fable', callback_data='voice3')
            voice4 = types.InlineKeyboardButton(text='👨‍🦱Onyx', callback_data='voice4')
            voice5 = types.InlineKeyboardButton(text='👩Nova', callback_data='voice5')
            voice6 = types.InlineKeyboardButton(text='👩‍🦱Shimmer', callback_data='voice6')
            user_back_button = types.InlineKeyboardButton(text="↩Back to menu", callback_data='back_user_from_voice')
            voice_model_menu.add(voice1, voice2, voice3, voice4, voice5, voice6, user_back_button)
            return voice_model_menu
        if interface == 'user_back':
            user_back_button = types.InlineKeyboardButton(text="↩Back to menu", callback_data='back_user')
            user_back.add(user_back_button)
            return user_back
        if interface == 'close_msg':
            close_msg_button = types.InlineKeyboardButton(text="❌Close", callback_data='close_msg')
            close_msg.add(close_msg_button)
            return close_msg
        if interface == 'chat_settings':
            if db_results[14]:
                voice_button = types.InlineKeyboardButton(text='🔇Turn off voice responses', callback_data='voice_off')
            else:
                voice_button = types.InlineKeyboardButton(text='🔈Enable voice responses', callback_data='voice_on')
            end_chat = types.InlineKeyboardButton(text="🔴End chat", callback_data='end_chat')
            chat_settings.add(voice_button, end_chat)
            return chat_settings
        if interface == 'chats_menu':
            chats_menu = types.InlineKeyboardMarkup(row_width=1)
            all_msgs = types.InlineKeyboardButton(text='💬Get all chats', callback_data='get_all_chats')
            get_chat = types.InlineKeyboardButton(text='🗨️Get a specific chat', callback_data='get_one_chat')
            delete_history = types.InlineKeyboardButton(text='🗑️Delete message history', callback_data='delete_history')
            user_back_button = types.InlineKeyboardButton(text="↩Back to menu", callback_data='back_user')
            chats_menu.add(all_msgs, get_chat, delete_history, user_back_button)
            return chats_menu
        if interface == 'chats_menu_text':
            return chats_menu_text_en
        if interface == 'input_chat_number':
            return chat_input_text_en
        if interface == 'your_chat_one_text':
            return your_chat_one_en
        if interface == 'error_get_chat':
            return error_get_chat_text_en
        if interface == 'delete_history_complete':
            return delete_history_complete_en
        if interface == 'price_info':
            return price_en
        if interface == 'image_generation_start':
            return image_generation_start_en
        if interface == 'img_generation':
            return img_generation_en
        if interface == 'terms_text':
            return terms_of_use_en
        if interface == 'welcome_text':
            return welcome_message_en
        if interface == 'pay_balance_text':
            return pay_balance_msg_en
        if interface == 'update_text':
            return update_en
        if interface == 'error_text':
            return error_openai_en
        if interface == 'error_unknow_text':
            return error_unkown_en
        if interface == 'error_unknow2_text':
            return error_unkown2_en
        if interface == 'error_text_msg':
            return error_text_msg_en
        if interface == 'error_delete_msg':
            return error_delete_msg_en
        if interface == 'bot_out':
            return bot_out_en
        if interface == 'wait_msg':
            return wait_msg_en
        if interface == 'end_chat_text':
            return chat_end_text_en
        if interface == 'your_chat_text':
            return your_chat_en
        if interface == 'your_chats_text':
            return your_chats_en
        if interface == 'error_create_chat':
            return error_create_chat_en
        if interface == 'welcome_chat_text':
            return hello_i_ai_en
        if interface == 'instruction_text':
            return instruction_msg_en
        if interface == 'error_summ':
            return error_summ_en
        if interface == 'success_changed_country':
            return success_country_changed_en
        if interface == 'success_ai_voice_changed':
            return success_ai_voice_changed_en
        if interface == 'russia_country':
            return "Russia"
        if interface == 'kazakhstan_country':
            return "Kazakhstan"
        if interface == 'ukraina_country':
            return "Ukraine"
        if interface == 'other_country':
            return "???"
        if interface == 'your_transactions_text':
            return your_transactions_en
        if interface == "insufficient_funds":
            return error_money_en
        if interface == 'subscribe_invite':
            return subscribe_invite_en
        if interface == 'subscribe_menu':
            menu = types.InlineKeyboardMarkup(row_width=1)
            subscribe_button = types.InlineKeyboardButton(text='💎Subscribe!', url=url_channel)
            subscribed_button = types.InlineKeyboardButton(text='✅Subscribed!', callback_data='subscribed')
            menu.add(subscribe_button, subscribed_button)
            return menu
        if interface == 'subscribe_warning':
            menu = types.InlineKeyboardMarkup(row_width=1)
            subscribe_button = types.InlineKeyboardButton(text='💎Subscribe!', url=url_channel)
            close_msg_button = types.InlineKeyboardButton(text="❌Close", callback_data='close_msg')
            menu.add(subscribe_button, close_msg_button)
            return menu
        if interface == 'error_openai_load':
            return error_openai_load_en
        if interface == 'pay_desc':
            return pay_desc_en
        if interface == 'empty_voice':
            return voice_empty_en
        if interface == 'voice_message':
            return voice_message_en
        if interface == 'recognize_voice':
            return recognize_voice_en
        if interface == 'rashod':
            if country == "Россия":
                return rashod_en.format("₽", "₽", "₽", "₽", "₽")
            elif country == "Казахстан":
                return rashod_en.format("₸", "₸", "₸", "₸", "₸")
            elif country == "Украина":
                return rashod_en.format("₴", "₴", "₴", "₴", "₴")
            else:
                return rashod_en.format("$", "$", "$", "$", "$")
        if interface == 'change_ai_model_text':
            return change_ai_model_en
        if interface == 'change_ai_model_markup':
            user_back_button = types.InlineKeyboardButton(text="↩Back to menu", callback_data='back_user')
            change_ai_model_markup.row_width = 1
            change_ai_model_markup.add(user_back_button)
            return change_ai_model_markup
        if interface == 'success_changed_ai_model':
            return success_ai_model_changed_en
        if interface == 'process_transactions':
            return process_file_operation_en
        if interface == 'process_chats':
            return process_file_chats_en
        if interface == 'photo_gpt':
            return use_gpt4_en

# Общение с БД
conn = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db
)
conn.autocommit = True
cursor = conn.cursor()

def db_insert_users(user_id: int, user_name: str, user_surname: str, username: str, refferer: int, date_reg):
    cursor.execute(
        'INSERT INTO users (user_id, user_name, user_surname, username, reffer, date_reg) VALUES (%s, %s, %s, %s, %s, %s)',
        (user_id, user_name, user_surname, username, refferer, date_reg)
    )

def db_insert_aaq(user_id, question, answer,
                  message_id, date_time, info_spending, model,
                  free_api, photo_user=None, voice_user=None, photo_bot=None, voice_bot=None):
    id_chat = 0
    cursor.execute(
        f"SELECT MAX(id_chat) FROM history_question_answer WHERE user_id = {user_id}"
    )
    is_first = cursor.fetchone()
    cursor.execute(
        f"SELECT MAX(id_chat) FROM history_question_answer WHERE user_id = {user_id} AND status_chat = {False}")
    chats = cursor.fetchone()
    if is_first[0] == None:
        id_chat = 1
    elif chats[0] != None:
        id_chat = chats[0]
    else:
        id_chat = int(is_first[0]) + 1
    cursor.execute(
        'INSERT INTO history_question_answer (user_id, id_chat, question, answer, message_id, date_time, spending, model, free_api, photo_user, voice_user, photo_bot, voice_bot) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
        (user_id, id_chat, question, answer, message_id, date_time, info_spending, model, free_api, photo_user,
         voice_user, photo_bot, voice_bot)
    )
    cursor.execute(
        'INSERT INTO history_question_answer_admin (user_id, id_chat, question, answer, message_id, date_time, spending, model, free_api, photo_user, voice_user, photo_bot, voice_bot) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
        (user_id, id_chat, question, answer, message_id, date_time, info_spending, model, free_api, photo_user,
         voice_user, photo_bot, voice_bot)
    )

def db_insert_transactions(user_id, type, merchant_order_id, amount, currency, status, date, menu_id, referal,
                           chat_number):
    cursor.execute(
        'INSERT INTO transactions_history (user_id, type, merchant_order_id, amount, currency, date_payment, status, pay_message, referal, chat_number) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
        (user_id, type, merchant_order_id, amount, currency, date, status, menu_id, referal, chat_number)
    )

def db_all_get(req):
    cursor.execute(req)
    return cursor.fetchall()[0]

def db_get(req):
    cursor.execute(req)
    return cursor.fetchone()[0]

def db_set(req):
    cursor.execute(req)

def db_check_exist(user_id: int):
    cursor.execute("SELECT user_id FROM users WHERE user_id=%s", (user_id,))
    result = cursor.fetchall()
    return result


# функции ChatGPT
def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        "gpt-4-vision-preview"
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            try:
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
            except:
                pass
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

def balance_out(total_price, user_id):
    db_results = db_all_get(f"SELECT * FROM users WHERE user_id = {user_id}")
    balance = db_results[9]
    country = db_results[11]
    cours_currency = db_get(f"SELECT cours_currency FROM settings").split('-')
    if country == 'Россия':
        rashod = float(total_price) * float(cours_currency[0])
    elif country == 'Казахстан':
        rashod = float(total_price) * float(cours_currency[1])
    elif country == 'Украина':
        rashod = float(total_price) * float(cours_currency[2])
    else:
        rashod = float(total_price)
    new_balance = round(float(balance) - float(rashod), 3)
    db_set(f"UPDATE users SET balance = {new_balance} WHERE user_id = {user_id}")
    return new_balance, rashod

def get_ai_answer(messages: list, user_id):
    base_prompt = [{"role": "system", "content": system_prompt_paid}]
    db_result = db_all_get(f"SELECT * FROM users WHERE user_id = {user_id}")
    model = db_result[12]
    balance = db_result[9]
    if model == "gpt-4-vision-preview":
        price_model = db_get(f"SELECT gpt4 FROM settings")
    else:
        price_model = db_get(f"SELECT gpt3 FROM settings")
    input_price_admin = float(price_model.split('-')[0])
    output_price_admin = float(price_model.split('-')[1])
    input_tokens_temp = float(num_tokens_from_messages(base_prompt + messages))
    input_price_temp = (input_tokens_temp / 1000) * input_price_admin
    info = 'None'
    country = db_result[11]
    cours_currency = db_get(f"SELECT cours_currency FROM settings").split('-')
    if country == "Россия":
        cours = cours_currency[0]
    elif country == "Казахстан":
        cours = cours_currency[1]
    elif country == "Украина":
        cours = cours_currency[2]
    else:
        cours = cours_currency[3]
    if input_price_temp > float(balance) / float(cours):
        return False, get_interface(user_id, "insufficient_funds"), info, False
    try:
        try:
            base_prompt = [{"role": "system", "content": system_prompt_free}]
            info_settings = db_all_get("SELECT * FROM settings")
            if not info_settings[16]:
                raise Exception("Use paid API")
            else:
                openai.api_key = token_free
                openai.base_url = free_api
                completion = openai.chat.completions.create(
                    model=model,
                    messages=base_prompt + messages,
                    max_tokens=info_settings[1],
                    temperature=info_settings[2]
                )
                input_token = float(completion.usage.prompt_tokens)
                output_token = float(completion.usage.completion_tokens)
                input_price = (input_token / 1000) * input_price_admin
                output_price = (output_token / 1000) * output_price_admin
                total_price = input_price + output_price
                new_balance, rashod = balance_out(total_price, user_id)
                if input_token != 0 and output_token != 0:
                    info = f"{input_token}~{output_token}~{rashod}~{new_balance}~{model}"
                else:
                    generated_msg = [{"role": "system",
                                      "content": completion.choices[0].message.content}]
                    output_token_temp2 = float(num_tokens_from_messages(base_prompt + generated_msg))
                    input_price = (input_tokens_temp / 1000) * input_price_admin
                    output_price = (output_token_temp2 / 1000) * output_price_admin
                    total_price = input_price + output_price
                    new_balance, rashod = balance_out(total_price, user_id)
                    info = f"{input_tokens_temp}~{output_token_temp2}~{rashod}~{new_balance}~{model}"
                return True, completion.choices[0].message.content, info, True
        except Exception as e:
            base_prompt = [{"role": "system", "content": system_prompt_paid}]
            openai.api_key = token
            openai.base_url = paid_api
            info_settings = db_all_get("SELECT * FROM settings")
            completion = openai.chat.completions.create(
                model=model,
                messages=base_prompt + messages,
                max_tokens=info_settings[1],
                temperature=info_settings[2]
            )
            input_token = float(completion.usage.prompt_tokens)
            output_token = float(completion.usage.completion_tokens)
            input_price = (input_token / 1000) * input_price_admin
            output_price = (output_token / 1000) * output_price_admin
            total_price = input_price + output_price
            new_balance, rashod = balance_out(total_price, user_id)
            info = f"{input_token}~{output_token}~{rashod}~{new_balance}~{model}"
            return True, completion.choices[0].message.content, info, False
    except openai.APIError:
        return False, get_interface(user_id, "error_text"), info, False
    except openai.BadRequestError:
        return False, get_interface(user_id, "error_openai_load"), info, False
    except Exception as e:
        print(str(e))
        return False, get_interface(user_id, "error_unknow_text"), info, False

def clear_messages(user_id):
    messages_path = os.path.join(f'{MESSAGES_DIR}/{user_id}/', f"{user_id}.txt")
    with open(messages_path, "w", encoding="utf-8") as f:
        f.truncate(0)

def get_messages(user_id):
    messages_path = os.path.join(f'{MESSAGES_DIR}/{user_id}/', f"{user_id}.txt")
    if os.path.getsize(messages_path) != 0:
        with open(messages_path, "r", encoding="utf-8") as f:
            messages = json.load(f)
        return messages
    else:
        return []

def set_messages(user_id, messages):
    os.makedirs(f'{MESSAGES_DIR}/{user_id}/', exist_ok=True)
    messages_path = os.path.join(f'{MESSAGES_DIR}/{user_id}/', f"{user_id}.txt")
    with open(messages_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False)

def create_message(role, text, photo_user=None):
    if photo_user == None:
        message = {"role": role, "content": text}
        return message
    else:
        message = {"role": "user",
                   "content": [
                       {"type": "text", "text": "В чем прикол этой фотографии?"},
                       {
                           "type": "image_url",
                           "image_url": {
                               "url": f"data:image/jpeg;base64,{photo_user}",
                           },
                       },
                   ]}
        return message

def get_chat(user_id):
    cursor.execute(f"SELECT MAX(id_chat) FROM history_question_answer WHERE user_id = {user_id}")
    id_chat = cursor.fetchone()[0]
    query = f"SELECT question, answer, spending, model, photo_user, voice_user, photo_bot, voice_bot FROM history_question_answer WHERE id_chat={id_chat} AND user_id = {user_id} ORDER BY date_time"
    cursor.execute(query)
    results = cursor.fetchall()
    language = db_get(f"SELECT language FROM users WHERE user_id = {user_id}")
    title = ''
    role = ''
    messages = ''
    spending = ''
    info_spending_text = ''
    info_total_spending_text = ''
    ai = ''
    user = ''
    audio_decode = 0
    tokens = 0
    tokens_price = 0
    total_price = 0
    currency = ""
    voice_price2 = 0
    image_price = 0
    photo_user = None
    voice_user = None
    photo_bot = None
    voice_bot = None
    if language == "Русский":
        title = 'История чатов'
        role = 'Роли'
        messages = 'Сообщения'
        spending = 'Траты'
        info_spending_text = '🎙️Расшифровка голосового сообщения: {} {}<br>' \
                             '🔊Озвучивание сообщения: {} {}<br>' \
                             '🖼️Генерация изображения: {} {}<br>' \
                             '🏷Токены: {} ~ {} {}<br>' \
                             '💸Потрачено: {} {}'
        info_total_spending_text = 'Итоговые затраты в данном чате:<br>' \
                                   '🎙️Расшифровка голосовых сообщений: {} {}<br>' \
                                   '🔊Озвучивание сообщениий: {} {}<br>' \
                                   '🖼️Генерация изображений: {} {}<br>' \
                                   '🏷Токены: {} ~ {} {}<br>' \
                                   '💸Всего потрачено: {} {}'
        ai = 'ИИ:'
        user = 'Вы:'
    if language == "Казахский":
        title = 'Чат тарихы'
        role = 'Рөлдері'
        messages = 'Хабарламалар'
        spending = 'Шығындар'
        info_spending_text = '🎙️Дауыстық хабарлама транскрипциясы: {} {}<br>' \
                             '🔊️Дауыстық хабарлама: {} {}<br>' \
                             '🖼️Кескінді құру: {} {}<br>' \
                             '🏷Токендер: {} ~ {} {}\n' \
                             '💸Жұмсалған: {} {}'
        info_total_spending_text = 'Осы чаттағы жалпы шығындар:\n' \
                                   '🎙️Дауыстық хабарламалардың транскрипциясы: {} {}<br>' \
                                   '🔊️Дауыстық хабарламалар: {} {}<br>' \
                                   '🖼️Кескінді құру: {} {}<br>' \
                                   '🏷Токендер: {} ~ {} {}<br>' \
                                   '💸Жалпы жұмсалған: {} {}'
        ai = 'ИИ:'
        user = 'Сіз:'
    if language == "Украинский":
        title = 'Історія чатів'
        role = 'Ролі'
        messages = 'Повідомлення'
        spending = 'Витрати'
        info_spending_text = '🎙️Розшифрування голосового повідомлення: {} {}<br>' \
                             '🔊Озвучування повідомлення: {} {}<br>' \
                             '🖼️Генерація зображення: {} {}<br>' \
                             '🏷Токени: {} ~ {} {}<br>' \
                             '💸Витрачено: {} {}'
        info_total_spending_text = 'Підсумкові витрати у цьому чаті:<br>' \
                                   '🎙️Розшифрування голосових повідомлень: {} {}<br>' \
                                   '🔊Озвучування повідомлень: {} {}<br>' \
                                   '🖼️Генерація зображення: {} {}<br>' \
                                   '🏷Токени: {} ~ {} {}<br>' \
                                   '💸Усього витрачено: {} {}'
        ai = 'ИИ:'
        user = 'Ви:'
    if language == "Английский":
        title = 'Chat history'
        role = 'Roles'
        messages = 'Messages'
        spending = 'Spending'
        info_spending_text = '🎙️Voice message transcript: {} {}<br>' \
                             '🔊Voice message: {} {}<br>' \
                             '🖼️Image generation: {} {}<br>' \
                             '🏷Tokens: {} ~ {} {}<br>' \
                             '💸Spent: {} {}'
        info_total_spending_text = 'Total costs in this chat:<br>' \
                                   '🎙️Transcription of voice messages: {} {}<br>' \
                                   '🔊Voice messages: {} {}<br>' \
                                   '🖼️Image generation: {} {}<br>' \
                                   '🏷Tokens: {} ~ {} {}<br>' \
                                   '💸Total Spent: {} {}'
        ai = 'AI:'
        user = 'You:'
    # Создаем HTML файл с перепиской
    html = f'''
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        '''
    html += '''
        <style>
            /* Стили для таблицы */
            table {
                border: 1px solid black;
                border-collapse: collapse; /* Убрать двойные границы */
            }

            /* Стили для заголовков таблицы */
            th {
                background-color: #D3D3D3;
                border: 1px solid black;
                padding: 5px;
            }

            /* Стили для ячеек таблицы */
            td {
                border: 1px solid black;
                padding: 5px;
            }

            /* Стили для ячеек с rowspan */
            td[rowspan="2"] {
                white-space: nowrap; /* Текст в ячейке не переносится */
                width: auto;        /* Ширина ячейки подстраивается под содержимое */
            }
        </style>
        '''
    html += f'''
    </head>
    <body>
        <h1>{title}</h1>
        <table>
            <tr>
                <th>{role}</th>
                <th>{messages}</th>
                <th>{spending}</th>
            </tr>
    '''

    for result in results:
        try:
            info_spending = result[2].split('~')
            audio_decode += round(float(info_spending[0]), 6)
            tokens += float(info_spending[1])
            tokens_price += float(info_spending[2])
            total_price += float(info_spending[3])
            currency = info_spending[5]
            voice_price2 += float(info_spending[6])
            image_price += float(info_spending[7])
            if result[3] == 'gpt-4-vision-preview':
                model = "GPT-4-TURBO<br>"
            elif result[3] == 'gpt-3.5-turbo':
                model = 'GPT-3.5-TURBO<br>'
            else:
                model = 'DALLE-3<br>'
            if result[4] != None:
                photo_user = image_to_base64(result[4])
            else:
                photo_user = None
            if result[5] != None:
                voice_user = audio_to_base64(result[5])
            else:
                voice_user = None
            if result[6] != None:
                photo_bot = image_to_base64(result[6])
            else:
                photo_bot = None
            if result[7] != None:
                voice_bot = audio_to_base64(result[7])
            else:
                voice_bot = None
            info_spending_html = f"🤖{model}\n{info_spending_text.format(round(float(info_spending[0]), 6), info_spending[5], float(info_spending[6]), info_spending[5], float(info_spending[7]), info_spending[5], float(info_spending[1]), float(info_spending[2]), info_spending[5], float(info_spending[3]), info_spending[5])}"
        except Exception as e:
            info_spending_html = f"{info_spending_text.format(0, '', 0, '', 0, '', 0, 0, '', 0, '')}"
        if (result[0] != "!") and (result[0] != "ERROR") and (result[1] != 'ERROR'):
            if photo_user != None and voice_user == None:
                html += f'''
                    <tr>
                        <td>{user}</td>
                        <td><img src="data:image/jpeg;base64,{photo_user}" style="width:350px;height:350px;"><br>{result[0]}</td>
                        <td rowspan="2" style="white-space: nowrap; width: auto;">{info_spending_html}</td>
                    </tr>
                    '''
            elif photo_user == None and voice_user != None:
                html += f'''
                        <tr>
                            <td>{user}</td>
                            <td><audio controls><source src="data:audio/mp3;base64,{voice_user}" type="audio/mp3">Ваш браузер не поддерживает аудио элемент.</audio><br>{result[0]}</td>
                            <td rowspan="2" style="white-space: nowrap; width: auto;"><br>{info_spending_html}</td>
                        </tr>
                        '''
            else:
                html += f'''
                        <tr>
                            <td>{user}</td>
                            <td>{result[0]}</td>
                            <td rowspan="2" style="white-space: nowrap; width: auto;">{info_spending_html}</td>
                        </tr>
                        '''
            if photo_bot != None and voice_bot == None:
                html += f'''
                    <tr>
                        <td>{ai}</td>
                        <td><img src="data:image/jpeg;base64,{photo_bot}" style="width:350px;height:350px;"><br>{process_code_blocks(result[1])}</td>
                    </tr>
                '''
            elif photo_bot == None and voice_bot != None:
                html += f'''
                    <tr>
                        <td>{ai}</td>
                        <td><audio controls><source src="data:audio/mp3;base64,{voice_bot}" type="audio/mp3">Ваш браузер не поддерживает аудио элемент.</audio><br>{process_code_blocks(result[1])}</td>
                    </tr>
                '''
            else:
                html += f'''
                        <tr>
                            <td>{ai}</td>
                            <td>{process_code_blocks(result[1])}</td>
                        </tr>
                    '''
        elif (result[0] == "ERROR") and (result[1] == 'ERROR'):
            pass
        else:
            html += f'''
                            <tr>
                                <td>{ai}</td>
                                <td>{process_code_blocks(result[1])}</td>
                                <td>-</td>
                            </tr>
                        '''

    try:
        info_spending_total_html = f"{info_total_spending_text.format(audio_decode, currency, voice_price2, currency, image_price, currency, tokens, tokens_price, currency, total_price, currency)}"
    except:
        info_spending_total_html = f"{info_total_spending_text.format(0, '', 0, '', 0, '', 0, 0, '', 0, '')}"
    html += f'''
            <tr>
                <td colspan="3">{info_spending_total_html}</td>
            </tr>
        </table>
    </body>
    </html>
    '''
    name_file = f'{MESSAGES_DIR}/{user_id}/chat_history{user_id}-{id_chat}.html'
    # Сохраняем HTML файл на диск
    with open(name_file, 'w', encoding="utf-8") as f:
        f.write(html)
    return name_file

def get_chat_settings(message, message_menu):
    try:
        bot.delete_message(chat_id=message_menu.chat.id, message_id=message_menu.id)
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    except:
        pass
    user_id = message.chat.id
    try:
        id_chat = int(message.text)
    except ValueError:
        bot.send_message(user_id, text=get_interface(user_id, 'error_get_chat'),
                         reply_markup=get_interface(user_id, 'user_back'))
        return
    query = f"SELECT question, answer, spending, model, photo_user, voice_user, photo_bot, voice_bot FROM history_question_answer WHERE id_chat={id_chat} AND user_id = {user_id} ORDER BY date_time"
    cursor.execute(query)
    results = cursor.fetchall()
    if results == []:
        bot.send_message(user_id, text=get_interface(user_id, 'error_get_chat'),
                         reply_markup=get_interface(user_id, 'user_back'))
        return
    language = db_get(f"SELECT language FROM users WHERE user_id = {user_id}")
    title = ''
    role = ''
    messages = ''
    spending = ''
    info_spending_text = ''
    info_total_spending_text = ''
    ai = ''
    user = ''
    audio_decode = 0
    tokens = 0
    tokens_price = 0
    total_price = 0
    currency = ""
    voice_price2 = 0
    image_price = 0
    photo_user = None
    voice_user = None
    photo_bot = None
    voice_bot = None
    if language == "Русский":
        title = 'История чатов'
        role = 'Роли'
        messages = 'Сообщения'
        spending = 'Траты'
        info_spending_text = '🎙️Расшифровка голосового сообщения: {} {}<br>' \
                             '🔊Озвучивание сообщения: {} {}<br>' \
                             '🖼️Генерация изображения: {} {}<br>' \
                             '🏷Токены: {} ~ {} {}<br>' \
                             '💸Потрачено: {} {}'
        info_total_spending_text = 'Итоговые затраты в данном чате:<br>' \
                                   '🎙️Расшифровка голосовых сообщений: {} {}<br>' \
                                   '🔊Озвучивание сообщениий: {} {}<br>' \
                                   '🖼️Генерация изображений: {} {}<br>' \
                                   '🏷Токены: {} ~ {} {}<br>' \
                                   '💸Всего потрачено: {} {}'
        ai = 'ИИ:'
        user = 'Вы:'
    if language == "Казахский":
        title = 'Чат тарихы'
        role = 'Рөлдері'
        messages = 'Хабарламалар'
        spending = 'Шығындар'
        info_spending_text = '🎙️Дауыстық хабарлама транскрипциясы: {} {}<br>' \
                             '🔊️Дауыстық хабарлама: {} {}<br>' \
                             '🖼️Кескінді құру: {} {}<br>' \
                             '🏷Токендер: {} ~ {} {}\n' \
                             '💸Жұмсалған: {} {}'
        info_total_spending_text = 'Осы чаттағы жалпы шығындар:\n' \
                                   '🎙️Дауыстық хабарламалардың транскрипциясы: {} {}<br>' \
                                   '🔊️Дауыстық хабарламалар: {} {}<br>' \
                                   '🖼️Кескінді құру: {} {}<br>' \
                                   '🏷Токендер: {} ~ {} {}<br>' \
                                   '💸Жалпы жұмсалған: {} {}'
        ai = 'ИИ:'
        user = 'Сіз:'
    if language == "Украинский":
        title = 'Історія чатів'
        role = 'Ролі'
        messages = 'Повідомлення'
        spending = 'Витрати'
        info_spending_text = '🎙️Розшифрування голосового повідомлення: {} {}<br>' \
                             '🔊Озвучування повідомлення: {} {}<br>' \
                             '🖼️Генерація зображення: {} {}<br>' \
                             '🏷Токени: {} ~ {} {}<br>' \
                             '💸Витрачено: {} {}'
        info_total_spending_text = 'Підсумкові витрати у цьому чаті:<br>' \
                                   '🎙️Розшифрування голосових повідомлень: {} {}<br>' \
                                   '🔊Озвучування повідомлень: {} {}<br>' \
                                   '🖼️Генерація зображення: {} {}<br>' \
                                   '🏷Токени: {} ~ {} {}<br>' \
                                   '💸Усього витрачено: {} {}'
        ai = 'ИИ:'
        user = 'Ви:'
    if language == "Английский":
        title = 'Chat history'
        role = 'Roles'
        messages = 'Messages'
        spending = 'Spending'
        info_spending_text = '🎙️Voice message transcript: {} {}<br>' \
                             '🔊Voice message: {} {}<br>' \
                             '🖼️Image generation: {} {}<br>' \
                             '🏷Tokens: {} ~ {} {}<br>' \
                             '💸Spent: {} {}'
        info_total_spending_text = 'Total costs in this chat:<br>' \
                                   '🎙️Transcription of voice messages: {} {}<br>' \
                                   '🔊Voice messages: {} {}<br>' \
                                   '🖼️Image generation: {} {}<br>' \
                                   '🏷Tokens: {} ~ {} {}<br>' \
                                   '💸Total Spent: {} {}'
        ai = 'AI:'
        user = 'You:'
    # Создаем HTML файл с перепиской
    html = f'''
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            '''
    html += '''
            <style>
                /* Стили для таблицы */
                table {
                    border: 1px solid black;
                    border-collapse: collapse; /* Убрать двойные границы */
                }

                /* Стили для заголовков таблицы */
                th {
                    background-color: #D3D3D3;
                    border: 1px solid black;
                    padding: 5px;
                }

                /* Стили для ячеек таблицы */
                td {
                    border: 1px solid black;
                    padding: 5px;
                }

                /* Стили для ячеек с rowspan */
                td[rowspan="2"] {
                    white-space: nowrap; /* Текст в ячейке не переносится */
                    width: auto;        /* Ширина ячейки подстраивается под содержимое */
                }
            </style>
            '''
    html += f'''
        </head>
        <body>
            <h1>{title}</h1>
            <table>
                <tr>
                    <th>{role}</th>
                    <th>{messages}</th>
                    <th>{spending}</th>
                </tr>
        '''

    for result in results:
        try:
            info_spending = result[2].split('~')
            audio_decode += round(float(info_spending[0]), 6)
            tokens += float(info_spending[1])
            tokens_price += float(info_spending[2])
            total_price += float(info_spending[3])
            currency = info_spending[5]
            voice_price2 += float(info_spending[6])
            image_price += float(info_spending[7])
            if result[3] == 'gpt-4-vision-preview':
                model = "GPT-4-TURBO<br>"
            elif result[3] == 'gpt-3.5-turbo':
                model = 'GPT-3.5-TURBO<br>'
            else:
                model = 'DALLE-3<br>'
            if result[4] != None:
                photo_user = image_to_base64(result[4])
            else:
                photo_user = None
            if result[5] != None:
                voice_user = audio_to_base64(result[5])
            else:
                voice_user = None
            if result[6] != None:
                photo_bot = image_to_base64(result[6])
            else:
                photo_bot = None
            if result[7] != None:
                voice_bot = audio_to_base64(result[7])
            else:
                voice_bot = None
            info_spending_html = f"🤖{model}\n{info_spending_text.format(round(float(info_spending[0]), 6), info_spending[5], float(info_spending[6]), info_spending[5], float(info_spending[7]), info_spending[5], float(info_spending[1]), float(info_spending[2]), info_spending[5], float(info_spending[3]), info_spending[5])}"
        except Exception as e:
            info_spending_html = f"{info_spending_text.format(0, '', 0, '', 0, '', 0, 0, '', 0, '')}"
        if (result[0] != "!") and (result[0] != "ERROR") and (result[1] != 'ERROR'):
            if photo_user != None and voice_user == None:
                html += f'''
                        <tr>
                            <td>{user}</td>
                            <td><img src="data:image/jpeg;base64,{photo_user}" style="width:350px;height:350px;"><br>{result[0]}</td>
                            <td rowspan="2" style="white-space: nowrap; width: auto;">{info_spending_html}</td>
                        </tr>
                        '''
            elif photo_user == None and voice_user != None:
                html += f'''
                            <tr>
                                <td>{user}</td>
                                <td><audio controls><source src="data:audio/mp3;base64,{voice_user}" type="audio/mp3">Ваш браузер не поддерживает аудио элемент.</audio><br>{result[0]}</td>
                                <td rowspan="2" style="white-space: nowrap; width: auto;"><br>{info_spending_html}</td>
                            </tr>
                            '''
            else:
                html += f'''
                            <tr>
                                <td>{user}</td>
                                <td>{result[0]}</td>
                                <td rowspan="2" style="white-space: nowrap; width: auto;">{info_spending_html}</td>
                            </tr>
                            '''
            if photo_bot != None and voice_bot == None:
                html += f'''
                        <tr>
                            <td>{ai}</td>
                            <td><img src="data:image/jpeg;base64,{photo_bot}" style="width:350px;height:350px;"><br>{process_code_blocks(result[1])}</td>
                        </tr>
                    '''
            elif photo_bot == None and voice_bot != None:
                html += f'''
                        <tr>
                            <td>{ai}</td>
                            <td><audio controls><source src="data:audio/mp3;base64,{voice_bot}" type="audio/mp3">Ваш браузер не поддерживает аудио элемент.</audio><br>{process_code_blocks(result[1])}</td>
                        </tr>
                    '''
            else:
                html += f'''
                            <tr>
                                <td>{ai}</td>
                                <td>{process_code_blocks(result[1])}</td>
                            </tr>
                        '''
        elif (result[0] == "ERROR") and (result[1] == 'ERROR'):
            pass
        else:
            html += f'''
                                <tr>
                                    <td>{ai}</td>
                                    <td>{process_code_blocks(result[1])}</td>
                                    <td>-</td>
                                </tr>
                            '''

    try:
        info_spending_total_html = f"{info_total_spending_text.format(audio_decode, currency, voice_price2, currency, image_price, currency, tokens, tokens_price, currency, total_price, currency)}"
    except:
        info_spending_total_html = f"{info_total_spending_text.format(0, '', 0, '', 0, '', 0, 0, '', 0, '')}"
    html += f'''
                <tr>
                    <td colspan="3">{info_spending_total_html}</td>
                </tr>
            </table>
        </body>
        </html>
        '''
    name_file = f'{MESSAGES_DIR}/{user_id}/chat_history{user_id}-{id_chat}.html'
    # Сохраняем HTML файл на диск
    with open(name_file, 'w', encoding="utf-8") as f:
        f.write(html)
    bot.send_document(user_id, document=open(name_file, 'rb'),
                      caption=get_interface(user_id, "your_chat_one_text"),
                      reply_markup=get_interface(user_id, "close_msg"))
    bot.send_message(user_id, text=get_interface(message.from_user.id, "welcome_text"),
                     parse_mode='Markdown',
                     reply_markup=get_interface(message.from_user.id, 'welcome'))

def generate_image(message, message_menu):
    if db_get(f"SELECT status_chat FROM users WHERE user_id = {message.chat.id}"):
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=message.id)
        except:
            pass
        bot.send_message(message.chat.id, get_interface(message.chat.id, 'error_create_chat'),
                         reply_markup=get_interface(message.chat.id, 'chat_settings'))
    else:
        print('Начал генерацию фото...')
        db_set(f"UPDATE users SET status_chat = {True} WHERE user_id = {message.chat.id}")
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db_insert_aaq(message.chat.id, '!', "IMAGE GENERATOR MODEL: DALLE-3", f'1-{message.chat.id}', time_now,
                      info_spending='-', model='gpt-4', free_api=False)

        openai.base_url = paid_api
        openai.api_key = token
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=message.id)
        except:
            pass
        bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id,
                              text=get_interface(message.chat.id, 'img_generation'))
        try:
            response = openai.images.generate(
                model="dall-e-3",
                prompt=message.text,
                size="1024x1024",
                quality="hd",
                n=1,
            )
            image_url = response.data[0].url
        except openai.BadRequestError:
            bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id,
                                  text=get_interface(message.chat.id, 'error_unknow_text'),
                                  reply_markup=get_interface(message.chat.id, 'user_back'))
            db_set(f"UPDATE users SET status_chat = {False} WHERE user_id = {message.chat.id}")
            db_set(f"UPDATE history_question_answer SET status_chat = {True} WHERE user_id = {message.chat.id}")
            return
        except openai.InternalServerError:
            bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id,
                                  text=get_interface(message.chat.id, 'error_unknow_text'),
                                  reply_markup=get_interface(message.chat.id, 'user_back'))
            db_set(f"UPDATE users SET status_chat = {False} WHERE user_id = {message.chat.id}")
            db_set(f"UPDATE history_question_answer SET status_chat = {True} WHERE user_id = {message.chat.id}")
            return
        try:
            bot.delete_message(chat_id=message_menu.chat.id, message_id=message_menu.id)
        except:
            pass
        language = db_get(f"SELECT language FROM users WHERE user_id = {message.chat.id}")
        price = db_get(f"SELECT dalle FROM settings;")
        balance, rashod = balance_out(price, message.chat.id)
        rashod = round(rashod, 3)
        country = db_get(f"SELECT country FROM users WHERE user_id = {message.chat.id}")
        if country == 'Россия':
            currency = '₽'
        elif country == 'Казахстан':
            currency = '₸'
        elif country == 'Украина':
            currency = '₴'
        else:
            currency = '$'
        if language == "Русский":
            caption = '✅Изображение готово!\n' \
                      f'✍️Ваш запрос(промпт): `{message.text}`\n' \
                      f'💸Расход: {rashod} {currency}\n' \
                      f'💰Баланс: {balance} {currency}'
        elif language == "Казахский":
            caption = '✅Сурет дайын!\n' \
                      f'✍️Сіздің сұранысыңыз (сұрау): `{message.text}`\n' \
                      f'💸Тұтыну: {rashod} {currency}\n' \
                      f'💰Баланс: {balance} {currency}'
        elif language == "Украинский":
            caption = '✅Зображення готове!\n' \
                      f'✍️Ваш запит(промпт): `{message.text}`\n' \
                      f'💸Витрата: {rashod} {currency}\n' \
                      f'💰Баланс: {balance} {currency}'
        else:
            caption = '✅The image is ready!\n' \
                      f'✍️Your request(prompt): `{message.text}`\n' \
                      f'💸Consumption: {rashod} {currency}\n' \
                      f'💰Balance: {balance} {currency}'
        name = f"{message.chat.id}-{random.randint(10000, 1000000)}"
        messages_path = os.path.join(f'{MESSAGES_DIR}/{message.chat.id}/', f"photo_{name}.jpg")
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(messages_path, 'wb') as file:
                file.write(response.content)
        msg = bot.send_photo(message.chat.id, photo=image_url, caption=caption, parse_mode='Markdown',
                             reply_markup=get_interface(message.chat.id, 'close_msg'))
        print(f"Сгенерировал изображение: {message.text} | User: {message.chat.id}")
        spend = f"0~0~0~{rashod}~0~{currency}~0~{rashod}"
        db_insert_aaq(message.chat.id, message.text, 'Image', f'{msg.message_id}-12', time_now, spend, 'dall-e-3',
                      False, None, None, messages_path, None)
        cursor.execute(f"SELECT MAX(id_chat) FROM history_question_answer WHERE user_id = {message.chat.id};")
        id_chat = cursor.fetchone()[0]
        db_set(f"UPDATE users SET status_chat = {False} WHERE user_id = {message.chat.id}")
        db_set(f"UPDATE history_question_answer SET status_chat = {True} WHERE user_id = {message.chat.id}")
        file = get_chat(message.chat.id)
        total_price_chat = get_chat_price(id_chat, message.chat.id)
        if total_price_chat > 0:
            country = db_get(f"SELECT country FROM users WHERE user_id = {message.chat.id}")
            if country == "Россия":
                currency = "RUB"
            elif country == "Казахстан":
                currency = "KZT"
            elif country == "Украина":
                currency = "UAH"
            else:
                currency = "USD"
            time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db_insert_transactions(message.chat.id, 6, None, total_price_chat, currency, True, time_now, None,
                                   None, id_chat)
        bot.send_document(message.chat.id, document=open(file, 'rb'),
                          caption=get_interface(message.chat.id, "your_chat_text"),
                          reply_markup=get_interface(message.chat.id, "close_msg"))
        bot.send_message(message.chat.id,
                         text=get_interface(message.from_user.id, "welcome_text"),
                         parse_mode='Markdown',
                         reply_markup=get_interface(message.from_user.id, 'welcome'))

# создание пользовательского меню
def create_info_menu(message):
    info_user = db_all_get(f"SELECT * FROM users WHERE user_id = {message.chat.id}")
    name = info_user[2]
    date_obj = info_user[5].date()
    formatted_date = date_obj.strftime('%d-%m-%Y')
    today = datetime.date.today()
    delta = (today - date_obj).days
    balance = info_user[9]
    referals = db_get(f"SELECT COUNT(user_id) FROM users WHERE reffer = {message.chat.id}")
    count_generated_msg = db_get(
        f"SELECT COUNT(user_id) FROM history_question_answer WHERE user_id = {message.chat.id} AND question != 'ERROR' AND question != '!' AND answer != 'ERROR'")
    count_chats = db_get(
        f"SELECT COUNT(DISTINCT id_chat) as unique_chats FROM history_question_answer WHERE user_id = {message.chat.id}")
    url_friends = f"{url_bot}?start={message.chat.id}"
    ai_model = info_user[12]
    ai_voice = info_user[13]
    country = info_user[11]
    currency2 = ""
    quer = ''
    if country == "Россия":
        quer = "russia_country"
        currency2 = "₽"
    if country == "Казахстан":
        quer = "kazakhstan_country"
        currency2 = "₸"
    if country == "Украина":
        quer = "ukraina_country"
        currency2 = "₴"
    if country == "Другое":
        quer = "other_country"
        currency2 = "$"
    language = info_user[10]
    info = ""
    if language == "Русский":
        info = f"🆔 {message.chat.id} | *{name}*\n" \
               f"├📅Дата регистрации: {formatted_date} ({format_days(delta, 1)})\n" \
               f"├💵Баланс: {balance} {currency2}\n" \
               f"├🤖ИИ модель: {ai_model}\n" \
               f"├🔊ИИ голос: {voice_lng_ru[ai_voice]}\n" \
               f"├✉Сгенерированных сообщений: {count_generated_msg} шт.\n" \
               f"├💬Количество чатов: {count_chats} шт.\n" \
               f"├🌐Страна: {get_interface(message.chat.id, quer)}\n" \
               f"├🗣Язык интерфейса: русский\n" \
               f"└👥Приведённых пользователей: {referals} чел.\n\n" \
               f"🔗Ссылка для друзей: `{url_friends}`"
    if language == "Казахский":
        info = f"🆔 {message.chat.id} | *{name}*\n" \
               f"├📅Тіркеу күні {formatted_date} ({format_days(delta, 2)})\n" \
               f"├💵Баланс: {balance} {currency2}\n" \
               f"├🤖AI моделі: {ai_model}\n" \
               f"├🔊AI дауысы: {voice_lng_kz[ai_voice]}\n" \
               f"├✉Жасалған хабарламалар: {count_generated_msg} зат.\n" \
               f"├💬Чаттар саны: {count_chats} зат.\n" \
               f"├🌐Тұрғылықты елі: {get_interface(message.chat.id, quer)}\n" \
               f"├🗣Интерфейс тілі: қазақ\n" \
               f"└👥Көрсетілген пайдаланушылар: {referals} адам.\n\n" \
               f"🔗Достар үшін сілтеме: `{url_friends}`"
    if language == "Украинский":
        info = f"🆔 {message.chat.id} | *{name}*\n" \
               f"├📅Дата реєстрації: {formatted_date} ({format_days(delta, 3)})\n" \
               f"├💵Баланс: {balance} {currency2}\n" \
               f"├🤖ІІ модель: {ai_model}\n" \
               f"├🔊ІІ голос: {voice_lng_ua[ai_voice]}\n" \
               f"├✉Створених повідомлень: {count_generated_msg} шт.\n" \
               f"├💬Кількість чатів: {count_chats} шт.\n" \
               f"├🌐Країна: {get_interface(message.chat.id, quer)}\n" \
               f"├🗣Мова інтерфейсу: українська\n" \
               f"└👥Наведених користувачів: {referals} чел.\n\n" \
               f"🔗Посилання для друзів: `{url_friends}`"
    if language == "Английский":
        info = f"🆔 {message.chat.id} | *{name}*\n" \
               f"├📅Date of registration: {formatted_date} ({format_days(delta, 4)})\n" \
               f"├💵Balance: {balance} {currency2}\n" \
               f"├🤖AI model: {ai_model}\n" \
               f"├🔊AI voice: {voice_lng_en[ai_voice]}\n" \
               f"├✉Generated messages: {count_generated_msg} pcs.\n" \
               f"├💬Number of chats: {count_chats} pcs.\n" \
               f"├🌐Country: {get_interface(message.chat.id, quer)}\n" \
               f"├🗣Interface language: English\n" \
               f"└👥Referred users: {referals} users.\n\n" \
               f"🔗Link for friends: `{url_friends}`"
    return info

def format_days(num_days, lng):
    if num_days % 10 == 1 and num_days % 100 != 11:
        if lng == 1:
            return f"{num_days} день"
        elif lng == 2:
            return f"{num_days} күн"
        elif lng == 3:
            return f"{num_days} день"
        elif lng == 4:
            return f"{num_days} day"
    elif num_days % 10 in [2, 3, 4] and num_days % 100 not in [12, 13, 14]:
        if lng == 1:
            return f"{num_days} дня"
        elif lng == 2:
            return f"{num_days} күн"
        elif lng == 3:
            return f"{num_days} дні"
        elif lng == 4:
            return f"{num_days} days"
    else:
        if lng == 1:
            return f"{num_days} дней"
        elif lng == 2:
            return f"{num_days} күн"
        elif lng == 3:
            return f"{num_days} днів"
        elif lng == 4:
            return f"{num_days} days"

def process_code_blocks(text):
    # Ищем первое вхождение ```
    start_idx = text.find("```")
    while start_idx != -1:
        # Ищем следующее слово после ```
        language = text[start_idx + 3:].split()[0]

        # Если язык программирования HTML, то изменяем класс на "language-html"
        if language.lower() == "html":
            language = "html"

        # Заменяем некоторые символы на их HTML-эквиваленты
        code = text[start_idx + 3 + len(language) + 1:]
        code = code.replace("<", "&lt;")
        code = code.replace(">", "&gt;")

        # Заменяем первое вхождение ``` на <pre><code class="language-{language}">
        text = text[:start_idx] + f"<pre><code class=\"language-{language}\">{code}"

        # Ищем последнее вхождение ```
        end_idx = text.find("```", start_idx + 3)
        if end_idx == -1:
            # Если блок кода не закрыт, добавляем </code></pre>
            text += "</code></pre>"
            break

        # Заменяем последнее вхождение ``` в блоке кода на </code></pre>
        text = text[:end_idx] + "</code></pre>" + text[end_idx + 3:]

        # Ищем следующее вхождение ```
        start_idx = text.find("```", end_idx)

    return text

def get_all_chats(user_id):
    cursor.execute(
        f"SELECT DISTINCT id_chat FROM history_question_answer WHERE user_id = {user_id} AND status_chat = {True} ORDER BY id_chat ASC;")
    id_chats = [row[0] for row in cursor.fetchall()]
    language = db_get(f"SELECT language FROM users WHERE user_id = {user_id}")
    title = ''
    chat_button = ''
    role = ''
    messages = ''
    spending = ''
    current_chat = ''
    info_spending_text = ''
    info_total_spending_text = ''
    ai = ''
    user = ''
    if language == "Русский":
        title = 'История чатов'
        chat_button = 'Чат'
        role = 'Роли'
        messages = 'Сообщения'
        spending = 'Траты'
        current_chat = 'Текущий чат:'
        info_spending_text = '🎙️Расшифровка голосового сообщения: {} {}<br>' \
                             '🔊️Озвучивание сообщения: {} {}<br>' \
                             '🖼️Генерация изображения: {} {}<br>' \
                             '🏷Токены: {} ~ {} {}<br>' \
                             '💸Потрачено: {} {}'
        info_total_spending_text = 'Итоговые затраты в данном чате:<br>' \
                                   '🎙️Расшифровка голосовых сообщений: {} {}<br>' \
                                   '🔊️Озвучивание сообщений: {} {}<br>' \
                                   '🖼️Генерация изображения: {} {}<br>' \
                                   '🏷Токены: {} ~ {} {}<br>' \
                                   '💸Всего потрачено: {} {}'
        ai = 'ИИ:'
        user = 'Вы:'
    if language == "Казахский":
        title = 'Чат тарихы'
        chat_button = 'Чат'
        role = 'Рөлдері'
        messages = 'Хабарламалар'
        spending = 'Шығындар'
        current_chat = 'Ағымдағы чат:'
        info_spending_text = '🎙️Дауыстық хабарлама транскрипциясы: {} {}<br>' \
                             '🔊️Дауыстық хабарлама: {} {}<br>' \
                             '🖼️Кескінді құру: {} {}<br>' \
                             '🏷Токендер: {} ~ {} {}<br>' \
                             '💸Жұмсалған: {} {}'
        info_total_spending_text = 'Осы чаттағы жалпы шығындар:<br>' \
                                   '🎙️Дауыстық хабарламалардың транскрипциясы: {} {}<br>' \
                                   '🔊️Дауыстық хабарламалар: {} {}<br>' \
                                   '🖼️Кескінді құру: {} {}<br>' \
                                   '🏷Токендер: {} ~ {} {}<br>' \
                                   '💸Жалпы жұмсалған: {} {}'
        ai = 'ИИ:'
        user = 'Сіз:'
    if language == "Украинский":
        title = 'Історія чатів'
        chat_button = 'Чат'
        role = 'Ролі'
        messages = 'Повідомлення'
        spending = 'Витрати'
        current_chat = 'Поточний чат:'
        info_spending_text = '🎙️Розшифрування голосового повідомлення: {} {}<br>' \
                             '🔊️Озвучування повідомлення: {} {}<br>' \
                             '🖼️Генерація зображення: {} {}<br>' \
                             '🏷Токени: {} ~ {} {}<br>' \
                             '💸Витрачено: {} {}'
        info_total_spending_text = 'Підсумкові витрати у цьому чаті:<br>' \
                                   '🎙️Розшифрування голосових повідомлень: {} {}<br>' \
                                   '🔊️Озвучування повідомлень: {} {}<br>' \
                                   '🖼️Генерація зображення: {} {}<br>' \
                                   '🏷Токени: {} ~ {} {}<br>' \
                                   '💸Усього витрачено: {} {}'
        ai = 'ИИ:'
        user = 'Ви:'
    if language == "Английский":
        title = 'Chat history'
        chat_button = 'Chat'
        role = 'Roles'
        messages = 'Messages'
        spending = 'Spending'
        current_chat = 'Current chat:'
        info_spending_text = '🎙️Voice message transcript: {} {}<br>' \
                             '🔊️Voice message: {} {}<br>' \
                             '🖼️Image generation: {} {}<br>' \
                             '🏷Tokens: {} ~ {} {}<br>' \
                             '💸Spent: {} {}'
        info_total_spending_text = 'Total costs in this chat:<br>' \
                                   '🎙️Transcription of voice messages: {} {}<br>' \
                                   '🔊️Voice messages: {} {}<br>' \
                                   '🖼️Image generation: {} {}<br>' \
                                   '🏷Tokens: {} ~ {} {}<br>' \
                                   '💸Total Spent: {} {}'
        ai = 'AI:'
        user = 'You:'

    buttons_html = "   ".join(
        [f'<button onclick="show_chat({id_chat})">{chat_button} {id_chat}</button>' for id_chat in id_chats])

    html = f'''
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>'''
    html += '''
        <style>
        .current-chat-label {{
            font-size: 20px; /* Измените размер шрифта по вашему усмотрению */
            font-weight: bold; /* Жирный стиль */
        }}
        .chat-number {{
            font-size: 20px; /* Измените размер шрифта по вашему усмотрению */
            font-weight: bold; /* Жирный стиль */
        }}
        td[rowspan="2"] {
            white-space: nowrap; /* Текст в ячейке не переносится */
            width: auto;        /* Ширина ячейки подстраивается под содержимое */
            border: 1px solid black; /* Границы для наглядности */
            padding: 5px; /* Отступы внутри ячеек */
        }
        </style>'''
    html += f'''
        <script>
            function show_chat(id_chat) {{
                var chats = document.getElementsByClassName('chat');
                for (var i = 0; i < chats.length; i++) {{
                    chats[i].style.display = 'none';
                }}
                var chat = document.getElementById('chat-' + id_chat);
                chat.style.display = 'table-row';
                // Добавляем номер текущего чата
                var chatNumber = document.getElementById('chat-number');
                chatNumber.innerHTML = '<span class="current-chat-label">{current_chat} </span>' + '<span class="chat-number">' + id_chat + '</span>';
            }}
        </script>
        <style>
        table, th, td {{
            border: 1px solid black;
            border-collapse: collapse;
            padding: 5px;
        }}
        th {{
            background-color: #D3D3D3;
        }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        {buttons_html}
        <div id="chat-number"></div>
    '''

    for id_chat in id_chats:
        query = f"SELECT question, answer, spending, model, photo_user, voice_user, photo_bot, voice_bot FROM history_question_answer WHERE id_chat={id_chat} AND user_id = {user_id} AND status_chat = {True} ORDER BY date_time"
        cursor.execute(query)
        results = cursor.fetchall()
        audio_decode = 0
        tokens = 0
        tokens_price = 0
        total_price = 0
        currency = ""
        voice_price2 = 0
        image_price = 0
        photo_user = None
        voice_user = None
        photo_bot = None
        voice_bot = None
        chat_html = f'''
        <table class="chat" id="chat-{id_chat}" style="display:none">
            <tr>
                <th>{role}</th>
                <th>{messages}</th>
                <th>{spending}</th>
            </tr>
        '''
        for result in results:
            try:
                info_spending = result[2].split('~')
                audio_decode += round(float(info_spending[0]), 6)
                tokens += float(info_spending[1])
                tokens_price += float(info_spending[2])
                total_price += float(info_spending[3])
                currency = info_spending[5]
                voice_price2 += float(info_spending[6])
                image_price += float(info_spending[7])
                if result[3] == 'gpt-4-vision-preview':
                    model = "GPT-4-TURBO<br>"
                elif result[3] == 'gpt-3.5-turbo':
                    model = 'GPT-3.5-TURBO<br>'
                else:
                    model = 'DALLE-3<br>'
                if result[4] != None:
                    photo_user = image_to_base64(result[4])
                else:
                    photo_user = None
                if result[5] != None:
                    voice_user = audio_to_base64(result[5])
                else:
                    voice_user = None
                if result[6] != None:
                    photo_bot = image_to_base64(result[6])
                else:
                    photo_bot = None
                if result[7] != None:
                    voice_bot = audio_to_base64(result[7])
                else:
                    voice_bot = None
                info_spending_html = f"🤖{model}\n{info_spending_text.format(float(info_spending[0]), info_spending[5], float(info_spending[6]), info_spending[5], float(info_spending[7]), info_spending[5], float(info_spending[1]), float(info_spending[2]), info_spending[5], float(info_spending[3]), info_spending[5])}"
            except Exception as e:
                info_spending_html = f"{info_spending_text.format(0, '', 0, '', 0, '', 0, 0, '', 0, '')}"
            if (result[0] != "!") and (result[0] != "ERROR") and (result[1] != 'ERROR'):
                if photo_user != None and voice_user == None:
                    chat_html += f'''
                        <tr>
                            <td>{user}</td>
                            <td><img src="data:image/jpeg;base64,{photo_user}" style="width:350px;height:350px;"><br>{result[0]}</td>
                            <td rowspan="2" style="white-space: nowrap; width: auto;">{info_spending_html}</td>
                        </tr>
                        '''
                elif photo_user == None and voice_user != None:
                    chat_html += f'''
                            <tr>
                                <td>{user}</td>
                                <td><audio controls><source src="data:audio/mp3;base64,{voice_user}" type="audio/mp3">Ваш браузер не поддерживает аудио элемент.</audio><br>{result[0]}</td>
                                <td rowspan="2" style="white-space: nowrap; width: auto;">{info_spending_html}</td>
                            </tr>
                            '''
                else:
                    chat_html += f'''
                            <tr>
                                <td>{user}</td>
                                <td>{result[0]}</td>
                                <td rowspan="2" style="white-space: nowrap; width: auto;">{info_spending_html}</td>
                            </tr>
                            '''
                if photo_bot != None and voice_bot == None:
                    chat_html += f'''
                        <tr>
                            <td>{ai}</td>
                            <td><img src="data:image/jpeg;base64,{photo_bot}" style="width:350px;height:350px;"><br>{process_code_blocks(result[1])}</td>
                        </tr>
                    '''
                elif photo_bot == None and voice_bot != None:
                    chat_html += f'''
                        <tr>
                            <td>{ai}</td>
                            <td><audio controls><source src="data:audio/mp3;base64,{voice_bot}" type="audio/mp3">Ваш браузер не поддерживает аудио элемент.</audio><br>{process_code_blocks(result[1])}</td>
                        </tr>
                    '''
                else:
                    chat_html += f'''
                            <tr>
                                <td>{ai}</td>
                                <td>{process_code_blocks(result[1])}</td>
                            </tr>
                        '''
            elif (result[0] == "ERROR") and (result[1] == 'ERROR'):
                pass
            else:
                chat_html += f'''
                    <tr>
                        <td>{ai}</td>
                        <td>{process_code_blocks(result[1])}</td>
                        <td>-</td>
                    </tr>
                '''
        try:
            info_spending_total_html = f"{info_total_spending_text.format(audio_decode, currency, voice_price2, currency, image_price, currency, tokens, tokens_price, currency, total_price, currency)}"
        except:
            info_spending_total_html = f"{info_total_spending_text.format(0, '', 0, '', 0, '', 0, 0, '', 0, '')}"
        chat_html += f'''
            <tr>
                <td colspan="3">{info_spending_total_html}</td>
            </tr>
        </table>
        '''
        html += chat_html

    html += '''
    </body>
    </html>
    '''
    name_file = f'{MESSAGES_DIR}/{user_id}/chats_history{user_id}.html'
    with open(name_file, 'w', encoding="utf-8") as f:
        f.write(html)
    return name_file

def get_all_transactions(user_id):
    # Получение информации о транзакциях пользователя из таблицы transactions_history
    cursor.execute(
        f"SELECT date_payment, type, amount, currency, status, merchant_order_id, referal, chat_number FROM transactions_history WHERE user_id={user_id}")
    rows = cursor.fetchall()
    language = db_get(f"SELECT language FROM users WHERE user_id = {user_id}")
    title = ''
    name = ''
    date_row = ''
    type_row = ''
    order_row = ''
    amount_row = ''
    currency_row = ''
    status_row = ''
    referal_row = ''
    chat_number_row = ''
    type_trans1 = ''
    type_trans2 = ''
    type_trans3 = ''
    type_trans4 = ''
    type_trans5 = ''
    type_trans6 = ''
    type_trans7 = ''
    success = ''
    not_success = ''
    if language == "Русский":
        title = 'Отчет о транзакциях'
        name = 'Отчет о транзакциях пользователя'
        date_row = 'Дата операции'
        type_row = 'Вид операции'
        order_row = 'Ордер платежа'
        referal_row = 'Реферал'
        chat_number_row = 'Номер чата'
        amount_row = 'Сумма операции'
        currency_row = 'Валюта'
        status_row = 'Статус операции'
        type_trans1 = 'Пополнение баланса'
        type_trans2 = 'Пополнение баланса с реферальной системы'
        type_trans3 = 'Пополнение баланса с пополнения реферала'
        type_trans4 = 'Ковертация средств(снятие)'
        type_trans5 = 'Ковертация средств(зачисление)'
        type_trans6 = 'Оплата чата'
        type_trans7 = 'Пополнение баланса от админа'
        success = 'Успешно!'
        not_success = "Операция не совершена!"
    if language == "Казахский":
        title = 'Транзакция туралы есеп'
        name = 'Пайдаланушы транзакциясы туралы есеп'
        date_row = 'Транзакция күні'
        type_row = 'Операция түрі'
        order_row = 'Төлем тәртібі'
        referal_row = 'Жолдама'
        chat_number_row = 'Чат нөмірі'
        amount_row = 'Транзакция сомасы'
        currency_row = 'Валюта'
        status_row = 'Жұмыс күйі'
        type_trans1 = 'Балансты толтыру'
        type_trans2 = 'Реферал жүйесінен теңгеріміңізді толтырыңыз'
        type_trans3 = 'Рефералды толтыру арқылы теңгеріміңізді толтырыңыз'
        type_trans4 = 'Қаражатты айырбастау (алу)'
        type_trans5 = 'Қаражатты айырбастау (несиелеу)'
        type_trans6 = 'Чат төлемі'
        type_trans7 = 'Әкімшіден балансты толтырыңыз'
        success = 'Сәтті!'
        not_success = "Операция аяқталмады!"
    if language == "Украинский":
        title = 'Звіт про транзакції'
        name = 'Звіт про транзакції користувача'
        date_row = 'Дата операції'
        type_row = 'Вид операції'
        order_row = 'Ордер платежу'
        referal_row = 'Реферал'
        chat_number_row = 'Номер чату'
        amount_row = 'Сума операції'
        currency_row = 'Валюта'
        status_row = 'Статус операції'
        type_trans1 = 'Поповнення балансу'
        type_trans2 = 'Поповнення балансу з реферальної системи'
        type_trans3 = 'Поповнення балансу з поповнення рефералу'
        type_trans4 = 'Ковертація коштів (обчислення)'
        type_trans5 = 'Ковертація коштів (зарахування)'
        type_trans6 = 'Оплата чату'
        type_trans7 = 'Поповнення балансу від адміну'
        success = 'Успішно!'
        not_success = "Операція не здійснена!"
    if language == "Английский":
        title = 'Transaction report'
        name = 'User transaction report'
        date_row = 'Date of operation'
        type_row = 'Type of operation'
        order_row = 'Payment order'
        referal_row = 'Referral'
        chat_number_row = 'Chat number'
        amount_row = 'Transaction amount'
        currency_row = 'Currency'
        status_row = 'Operation status'
        type_trans1 = 'Balance replenishment'
        type_trans2 = 'Top up your balance using the referral system'
        type_trans3 = 'Top up your balance by topping up your referral'
        type_trans4 = 'Funds conversion (calculation)'
        type_trans5 = 'Funds conversion (crediting)'
        type_trans6 = 'Chat payment'
        type_trans7 = 'Top up balance from admin'
        success = 'Successfully!'
        not_success = "Operation not completed!"

    # Формирование HTML-отчета
    report = f'<html><head><meta charset="UTF-8"><title>{title}</title></head><body>'
    report += f"<h1>{name} " + str(user_id) + "</h1>"
    report += f"<table border='1'><tr><th>{date_row}</th><th>{type_row}</th><th>{order_row}</th><th>{referal_row}</th><th>{chat_number_row}</th><th>{amount_row}</th><th>{currency_row}</th><th>{status_row}</th></tr>"
    type_trans = ''
    for row in rows:
        if row[1] == 1:
            type_trans = type_trans1
        if row[1] == 2:
            type_trans = type_trans2
        if row[1] == 3:
            type_trans = type_trans3
        if row[1] == 4:
            type_trans = type_trans4
        if row[1] == 5:
            type_trans = type_trans5
        if row[1] == 6:
            type_trans = type_trans6
        if row[1] == 7:
            type_trans = type_trans7
        if row[4]:
            status = success
        else:
            status = not_success
        if row[5] == None:
            order_id = "-"
        else:
            order_id = str(row[5])
        if row[6] == None:
            referal = '-'
        else:
            referal = str(row[6])
        if row[7] == None:
            chat_number = '-'
        else:
            if language == "Английский":
                chat_number = f"Chat-{row[7]}"
            else:
                chat_number = f"Чат-{row[7]}"
        # Конвертация даты из формата SQLite в формат dd.mm.yyyy
        date_str = datetime.datetime.strptime(str(row[0]), '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y %H:%M:%S')
        report += "<tr><td>" + date_str + "</td><td>" + type_trans + "</td><td>" + order_id + "</td><td>" + referal + "</td><td>" + chat_number + "</td><td>" + str(
            row[2]) + "</td><td>" + str(row[
                                            3]) + "</td><td>" + status + "</td></tr>"
    report += "</table></body></html>"

    # Создание файла и запись в него отчета
    file_name = f'{MESSAGES_DIR}/{user_id}/transaction_report_user_{user_id}.html'
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(report)

    return file_name


# платежная система
def get_pay_button(user_id):
    info_pay = db_all_get(f"SELECT * FROM settings")
    country = db_get(f"SELECT country FROM users WHERE user_id = {user_id}")
    if country == "Россия":
        currency = "₽"
        pay1 = info_pay[7].split("-")[0]
        pay2 = info_pay[8].split("-")[0]
        pay3 = info_pay[9].split("-")[0]
        pay4 = info_pay[10].split("-")[0]
    elif country == "Казахстан":
        currency = "₸"
        pay1 = info_pay[7].split("-")[1]
        pay2 = info_pay[8].split("-")[1]
        pay3 = info_pay[9].split("-")[1]
        pay4 = info_pay[10].split("-")[1]
    elif country == "Украина":
        currency = "₴"
        pay1 = info_pay[7].split("-")[2]
        pay2 = info_pay[8].split("-")[2]
        pay3 = info_pay[9].split("-")[2]
        pay4 = info_pay[10].split("-")[2]
    else:
        currency = "$"
        pay1 = info_pay[7].split("-")[3]
        pay2 = info_pay[8].split("-")[3]
        pay3 = info_pay[9].split("-")[3]
        pay4 = info_pay[10].split("-")[3]
    pay = types.InlineKeyboardMarkup(row_width=2)
    pay.add(types.InlineKeyboardButton(text=f"{pay1} {currency}", callback_data="pay1_button"),
            types.InlineKeyboardButton(text=f"{pay2} {currency}", callback_data="pay2_button"),
            types.InlineKeyboardButton(text=f"{pay3} {currency}", callback_data="pay3_button"),
            types.InlineKeyboardButton(text=f"{pay4} {currency}", callback_data="pay4_button"))
    pay.row_width = 1
    language = db_get(f"SELECT language FROM users WHERE user_id = {user_id}")
    if language == "Русский":
        user_back_button = types.InlineKeyboardButton(text="↩Вернуться в меню", callback_data='back_user')
        pay.add(user_back_button)
    elif language == "Казахский":
        user_back_button = types.InlineKeyboardButton(text="↩Мәзірге оралу", callback_data='back_user')
        pay.add(user_back_button)
    elif language == "Украинский":
        user_back_button = types.InlineKeyboardButton(text="↩Повернутись до меню", callback_data='back_user')
        pay.add(user_back_button)
    else:
        user_back_button = types.InlineKeyboardButton(text="↩Back to menu", callback_data='back_user')
        pay.add(user_back_button)
    return pay

def create_payment(message, message_menu):
    global summ_user
    error_summ = get_interface(message.chat.id, 'error_summ')
    country = db_get(f"SELECT country FROM users WHERE user_id = {message.chat.id}")
    if country == "Россия":
        min_amount = 10
    elif country == "Казахстан":
        min_amount = 35
    elif country == "Украина":
        min_amount = 35
    else:
        min_amount = 1
    try:
        summ_user = int(message.text)
        if summ_user < min_amount:
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=message.id)
            except:
                pass
            bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id,
                                  text=error_summ,
                                  reply_markup=get_interface(message.from_user.id, 'user_back'))
            return
    except ValueError:
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=message.id)
        except:
            pass
        bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id,
                              text=error_summ,
                              reply_markup=get_interface(message.from_user.id, 'user_back'))
        return
    order_pay_id = random.randint(1000, 1000000)
    order_merchant_id = str(message.chat.id) + "-" + str(order_pay_id)
    desc = get_interface(message.chat.id, 'pay_desc')
    if country == "Россия":
        currency = "RUB"
        currency2 = "₽"
        url_pay = create_link_yookassa(summ_user, currency, order_merchant_id, desc)
    elif country == "Казахстан":
        currency = "KZT"
        currency2 = "₸"
        url_pay = get_url_robokassa(summ_user, order_merchant_id, currency, desc)
    elif country == "Украина":
        currency = "UAH"
        currency2 = "₴"
        amount2 = round(summ_user * get_exchange_rate('UAH', 'USD'), 1)
        url_pay = get_url_robokassa(amount2, order_merchant_id, 'USD', desc)
    else:
        currency = "USD"
        currency2 = "$"
        url_pay = get_url_robokassa(summ_user, order_merchant_id, currency, desc)
    payment = types.InlineKeyboardMarkup()
    payment.row_width = 1
    language = db_get(f"SELECT language FROM users WHERE user_id = {message.chat.id}")
    if language == "Русский":
        pay_button = types.InlineKeyboardButton(text=f"Оплатить {summ_user} {currency2}", url=f"{url_pay}")
        user_back_button = types.InlineKeyboardButton(text="↩Вернуться в меню", callback_data='back_user')
        payment.add(pay_button, user_back_button)
        bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id,
                              text=f"Перейдите к оплате, на сумму {summ_user} {currency2}\nПосле успешной оплаты, бот уведомит вас!",
                              reply_markup=payment)
    elif language == "Казахский":
        pay_button = types.InlineKeyboardButton(text=f"{summ_user} {currency2} төлеңіз", url=f"{url_pay}")
        user_back_button = types.InlineKeyboardButton(text="↩Мәзірге оралу", callback_data='back_user')
        payment.add(pay_button, user_back_button)
        bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id,
                              text=f"{summ_user} {currency2} мөлшерінде төлемді жалғастырыңыз.\nСәтті төлемнен кейін бот сізге хабарлайды!",
                              reply_markup=payment)
    elif language == "Украинский":
        pay_button = types.InlineKeyboardButton(text=f"Сплатити {summ_user} {currency2}", url=f"{url_pay}")
        user_back_button = types.InlineKeyboardButton(text="↩Повернутись до меню", callback_data='back_user')
        payment.add(pay_button, user_back_button)
        bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id,
                              text=f"Перейдіть до оплати, у сумі {summ_user} {currency2}\nПісля успішної оплати,"
                                   f" бот повідомить вас!",
                              reply_markup=payment)
    else:
        pay_button = types.InlineKeyboardButton(text=f"Pay {summ_user} {currency2}", url=f"{url_pay}")
        user_back_button = types.InlineKeyboardButton(text="↩Back to menu", callback_data='back_user')
        payment.add(pay_button, user_back_button)
        bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id,
                              text=f"Proceed to payment, in the amount of {summ_user} {currency2}\nAfter successful"
                                   f" payment, the bot will notify you!",
                              reply_markup=payment)
    try:
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    except:
        pass
    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message_menu_id = str(message.chat.id) + "-" + str(message_menu.id)
    db_insert_transactions(message.chat.id, 1, order_merchant_id, summ_user, currency, False, time_now, message_menu_id,
                           None, None)

def create_payment2(message, button):
    order_pay_id = random.randint(1000, 1000000)
    order_merchant_id = str(message.chat.id) + "-" + str(order_pay_id)
    country = db_get(f"SELECT country FROM users WHERE user_id = {message.chat.id}")
    desc = get_interface(message.chat.id, 'pay_desc')
    if country == "Россия":
        currency = "RUB"
        currency2 = "₽"
        index_pay = 0
        amount = db_get(f"SELECT {button} FROM settings").split('-')[index_pay]
        url_pay = create_link_yookassa(amount, currency, order_merchant_id, desc)
    elif country == "Казахстан":
        currency = "KZT"
        currency2 = "₸"
        index_pay = 1
        amount = db_get(f"SELECT {button} FROM settings").split('-')[index_pay]
        url_pay = get_url_robokassa(amount, order_merchant_id, currency, desc)
    elif country == "Украина":
        currency = "UAH"
        currency2 = "₴"
        index_pay = 2
        amount = db_get(f"SELECT {button} FROM settings").split('-')[index_pay]
        amount2 = round(float(amount) * get_exchange_rate('UAH', 'USD'), 1)
        url_pay = get_url_robokassa(amount2, order_merchant_id, "USD", desc)
    else:
        currency = "USD"
        currency2 = "$"
        index_pay = 3
        amount = db_get(f"SELECT {button} FROM settings").split('-')[index_pay]
        url_pay = get_url_robokassa(amount, order_merchant_id, currency, desc)

    payment = types.InlineKeyboardMarkup(row_width=1)
    language = db_get(f"SELECT language FROM users WHERE user_id = {message.chat.id}")
    if language == "Русский":
        pay_button = types.InlineKeyboardButton(text=f"Оплатить {amount} {currency2}", url=f"{url_pay}")
        user_back_button = types.InlineKeyboardButton(text="↩Вернуться в меню", callback_data='back_user')
        payment.add(pay_button, user_back_button)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                              text=f"Перейдите к оплате, на сумму {amount} {currency2}\nПосле успешной оплаты, бот уведомит вас!",
                              reply_markup=payment)
    elif language == "Казахский":
        pay_button = types.InlineKeyboardButton(text=f"{amount} {currency2} төлеу", url=f"{url_pay}")
        user_back_button = types.InlineKeyboardButton(text="↩Мәзірге оралу", callback_data='back_user')
        payment.add(pay_button, user_back_button)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                              text=f"{amount} {currency2} мөлшерінде төлемді жалғастырыңыз.\nСәтті төлемнен кейін бот сізге хабарлайды!",
                              reply_markup=payment)
    elif language == "Украинский":
        pay_button = types.InlineKeyboardButton(text=f"Сплатити {amount} {currency2}", url=f"{url_pay}")
        user_back_button = types.InlineKeyboardButton(text="↩Повернутись до меню", callback_data='back_user')
        payment.add(pay_button, user_back_button)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                              text=f"Перейдіть до оплати, у сумі {amount} {currency2}\nПісля успішної оплати,"
                                   f" бот повідомить вас!",
                              reply_markup=payment)
    else:
        pay_button = types.InlineKeyboardButton(text=f"Pay {amount} {currency2}", url=f"{url_pay}")
        user_back_button = types.InlineKeyboardButton(text="↩Back to menu", callback_data='back_user')
        payment.add(pay_button, user_back_button)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.id,
                              text=f"Proceed to payment, in the amount of {amount} {currency2}\nAfter successful"
                                   f" payment, the bot will notify you!",
                              reply_markup=payment)
    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message_menu_id = str(message.chat.id) + "-" + str(message.id)
    db_insert_transactions(message.chat.id, 1, order_merchant_id, amount, currency, False, time_now, message_menu_id,
                           None,
                           None)

def add_bonus(type, user_id, date, referal):
    if type == "reffer":
        country = db_get(f"SELECT country FROM users WHERE user_id = {user_id}")
        old_balance = db_get(f"SELECT balance FROM users WHERE user_id = {user_id}")
        refferer_bonus = db_get(f"SELECT reffer_bonus FROM settings").split('-')
        if country == 'Россия':
            bonus = int(refferer_bonus[0])
            currency = 'RUB'
        elif country == 'Казахстан':
            bonus = int(refferer_bonus[1])
            currency = 'KZT'
        elif country == 'Украина':
            bonus = int(refferer_bonus[2])
            currency = 'UAH'
        else:
            bonus = int(refferer_bonus[3])
            currency = 'USD'
        bonus_reffer = old_balance + bonus
        db_set(f"UPDATE users SET balance = {bonus_reffer} WHERE user_id = {user_id}")
        db_insert_transactions(user_id, 2, None, bonus_reffer, currency, True, date, None, referal, None)
        return bonus
    elif type == 'referal':
        country = db_get(f"SELECT country FROM users WHERE user_id = {user_id}")
        referal_bonus = db_get(f"SELECT referal_bonus FROM settings").split('-')
        old_bonus = db_get(f"SELECT balance FROM users WHERE user_id = {user_id}")
        if country == 'Россия':
            bonus = int(referal_bonus[0])
            currency = 'RUB'
        elif country == 'Казахстан':
            bonus = int(referal_bonus[1])
            currency = 'KZT'
        elif country == 'Украина':
            bonus = int(referal_bonus[2])
            currency = 'UAH'
        else:
            bonus = int(referal_bonus[3])
            currency = 'USD'
        bonus_referal = bonus + old_bonus
        db_set(f"UPDATE users SET balance = {bonus_referal} WHERE user_id = {user_id}")
        db_insert_transactions(user_id, 2, None, bonus_referal, currency, True, date, None, None, None)
        return bonus_referal

def get_exchange_rate(currency1, currency2):
    response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{currency1}")
    exchange_rate = response.json()['rates'][currency2]
    return exchange_rate

def convert(user_id, new_country):
    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    country = db_get(f"SELECT country FROM users WHERE user_id = {user_id}")
    if new_country != country:
        try:
            if country == 'Россия':
                currency1 = 'RUB'
            elif country == 'Казахстан':
                currency1 = 'KZT'
            elif country == 'Украина':
                currency1 = 'UAH'
            else:
                currency1 = 'USD'
            if new_country == 'Россия':
                currency2 = 'RUB'
            elif new_country == 'Казахстан':
                currency2 = 'KZT'
            elif new_country == 'Украина':
                currency2 = 'UAH'
            else:
                currency2 = 'USD'
            balance_old = db_get(f"SELECT balance FROM users WHERE user_id = {user_id}")
            cours = get_exchange_rate(currency1, currency2)
            balance = round(balance_old * cours, 2) * 0.98
            db_set(f"UPDATE users SET balance = {balance} WHERE user_id = {user_id}")
            db_insert_transactions(user_id, 4, None, balance_old, currency1, True, time_now, None, None, None)
            db_insert_transactions(user_id, 5, None, balance, currency2, True, time_now, None, None, None)
            return True
        except Exception as e:
            print(str(e))
            return False
    else:
        return True

def payment_approved(order_id):
    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pay_info = order_id.split('-')
    amount = db_get(f"SELECT amount FROM transactions_history WHERE merchant_order_id = '{order_id}'")
    db_set(f"UPDATE transactions_history SET status = {True} WHERE merchant_order_id = '{order_id}'")
    info = db_all_get(f"SELECT * FROM users WHERE user_id = {pay_info[0]}")
    balance_user = info[9]
    referal = info[8]
    cashback_bonus = db_get(f"SELECT cashback FROM settings")
    menu_id = db_get(f"SELECT pay_message FROM transactions_history WHERE merchant_order_id = '{order_id}'").split('-')
    country_user = db_get(f"SELECT country FROM users WHERE user_id = {pay_info[0]}")
    currency_user = ""
    currency_user2 = ""
    if country_user == "Россия":
        currency_user = "RUB"
        currency_user2 = "₽"
    if country_user == "Казахстан":
        currency_user = "KZT"
        currency_user2 = "₸"
    if country_user == "Украина":
        currency_user = "UAH"
        currency_user2 = "₴"
    if country_user == "Другое":
        currency_user = "USD"
        currency_user2 = "$"
    if referal != 0:
        country_referal = db_get(f"SELECT country FROM users WHERE user_id = {referal}")
        currency_referal = ""
        if country_referal == "Россия":
            currency_referal = "RUB"
        if country_referal == "Казахстан":
            currency_referal = "KZT"
        if country_referal == "Украина":
            currency_referal = "UAH"
        if country_referal == "Другое":
            currency_referal = "USD"
        referal_bonus = db_get(f"SELECT balance FROM users WHERE user_id = {referal}")
        bonus = round((float(amount) * float(cashback_bonus)) / 100)
        if country_referal != country_user:
            cours = get_exchange_rate(currency_user, currency_referal)
            bonus = round(bonus * cours, 2)
        db_set(f"UPDATE users SET balance = {float(referal_bonus) + bonus} WHERE user_id = {referal}")
        db_insert_transactions(referal, 3, None, bonus, currency_referal, True, time_now, None, pay_info[0], None)
        language = db_get(f"SELECT language FROM users WHERE user_id = {pay_info[0]}")
        name_referal = db_get(f"SELECT user_name FROM users WHERE user_id = {pay_info[0]}")
        if language == "Русский":
            bot.send_message(referal,
                             text=f"Вам начислено {bonus} баллов за "
                                  f"пополнение баланса вашим рефералом({name_referal}).",
                             reply_markup=get_interface(pay_info[0], 'close_msg'))
        if language == "Казахский":
            bot.send_message(referal,
                             text=f"Сізге жолдама({name_referal}) арқылы балансты толтыру үшін {bonus} балдар берілді.",
                             reply_markup=get_interface(pay_info[0], 'close_msg'))
        if language == "Украинский":
            bot.send_message(referal,
                             text=f"Вам нараховано {bonus} балів за поповнення балансу вашим рефералом({name_referal}).",
                             reply_markup=get_interface(pay_info[0], 'close_msg'))
        if language == "Английский":
            bot.send_message(referal,
                             text=f"You are awarded {bonus} points for replenishing the balance by your referral({name_referal}).",
                             reply_markup=get_interface(pay_info[0], 'close_msg'))
    db_set(f"UPDATE users SET balance = {int(balance_user) + int(amount)} WHERE user_id = {pay_info[0]}")
    try:
        bot.delete_message(menu_id[0], menu_id[1])
    except:
        pass
    language = db_get(f"SELECT language FROM users WHERE user_id = {pay_info[0]}")
    if language == "Русский":
        bot.send_message(pay_info[0],
                         text=f"✅Ваш баланс пополнен!\n├Номер платежа: {order_id}\n└Сумма платежа: {amount} {currency_user2}",
                         reply_markup=get_interface(pay_info[0], "user_back"))
    if language == "Казахский":
        bot.send_message(pay_info[0],
                         text=f"✅Сіздің балансыңыз толтырылды!\n├Төлем нөмірі: {order_id}\n└Төлем сомасы: {amount} {currency_user2}",
                         reply_markup=get_interface(pay_info[0], "user_back"))
    if language == "Украинский":
        bot.send_message(pay_info[0],
                         text=f"✅Ваш баланс поповнено!\n├Номер платежу: {order_id}\n└Сума платежу: {amount} {currency_user2}",
                         reply_markup=get_interface(pay_info[0], "user_back"))
    if language == "Английский":
        bot.send_message(pay_info[0],
                         text=f"✅Your balance has been replenished!\n├Payment order: {order_id}\n└Amount of payment: {amount} {currency_user2}",
                         reply_markup=get_interface(pay_info[0], "user_back"))

# платежная система robokassa
def calculate_signature(*args) -> str:
    """Create signature MD5.
    """
    return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()

def get_url_robokassa(summ, order_info, currency, desc):
    order_info_parse = order_info.split('-')
    order_id = order_info_parse[1]
    Shp_id = f"Shp_id={order_info_parse[0]}"
    sign = calculate_signature(MerchantLogin, summ, order_id, currency, pass_test1, Shp_id)
    kassaurl = f"https://auth.robokassa.kz/Merchant/Index.aspx?MerchantLogin={MerchantLogin}&OutSum={summ}&InvoiceID={order_id}&OutSumCurrency={currency}&Description={desc}&Shp_id={order_info_parse[0]}&SignatureValue={sign}&Encoding=UTF-8"
    return kassaurl

def parse_response(request: str) -> dict:
    """
    :param request: Link.
    :return: Dictionary.
    """
    params = {}

    for item in request.split('&'):
        key, value = item.split('=')
        params[key] = value
    return params

def check_signature_result(
        order_number: int,  # invoice number
        received_sum: decimal.Decimal,  # cost of goods, RU
        received_signature: str,  # SignatureValue
        password: str,  # Merchant password
        Shp_id
) -> bool:
    signature = calculate_signature(received_sum, order_number, password, Shp_id)
    if signature.lower() == received_signature.lower():
        return True
    return False

# платежная система yookassa
def create_link_yookassa(amount, currency, order_info, desc):
    order_info_parse = order_info.split('-')
    order_id = order_info_parse[1]
    user_id = order_info_parse[0]
    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": currency
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/uai_robot"
        },
        "capture": True,
        "description": str(desc),
        "metadata": {
            "order_id": str(order_id),
            "user_id": str(user_id)
        },
        "receipt": {
            "customer": {
                "email": "dx.clyde@gmail.com"
            },
            "items": [
                {
                    "description": str(desc),
                    "quantity": "1",
                    "amount": {
                        "value": amount,
                        "currency": currency
                    },
                    "vat_code": "1"
                }]
        }
    }, uuid.uuid4())
    return payment.confirmation.confirmation_url

# админское меню
def create_info_adminmenu():
    count_users = db_get("SELECT COUNT(user_id) FROM users")
    info_settings = db_all_get("SELECT * FROM settings")
    if info_settings[0] == 1:
        status_bot = "работает"
    else:
        status_bot = "отключен"
    token_message = info_settings[1]
    temperature_model = info_settings[2]
    total_blocked = info_settings[3]
    bonus_reffer = info_settings[4]
    bonus_referal = info_settings[5]
    trial_bonus = info_settings[15]
    gpt4_price = info_settings[12]
    gpt3_price = info_settings[11]
    whisper_price = info_settings[13]
    cours_currency = info_settings[14]
    cashback = info_settings[6]
    if info_settings[16]:
        free_api = 'подключен'
    else:
        free_api = 'отключен'
    total_income, total_profit, total_use_gpt3, total_use_gpt4, total_use_free_api = finance_calculator()
    count_questions = int(total_use_gpt4) + int(total_use_gpt3)
    info = f"⚙Админ-панель\n" \
           f"├Количество пользователей: {count_users}\n" \
           f"├Состояние бота: {status_bot}\n" \
           f"├Токены на чат: {token_message} шт.\n" \
           f"├Температура модели: {temperature_model}\n" \
           f"├Бонус реферов: {bonus_reffer} баллов\n" \
           f"├Бонус рефералов: {bonus_referal} баллов\n" \
           f"├Триал бонус: {trial_bonus} баллов\n" \
           f"├GPT-4 прайс: {gpt4_price}\n" \
           f"├GPT-3.5-turbo прайс: {gpt3_price}\n" \
           f"├Whisper прайс: {whisper_price}\n" \
           f"├Курс валют: {cours_currency}\n" \
           f"├Кэшбек: {cashback} %\n" \
           f"├Бесплатный API: {free_api} \n" \
           f"├Всего потрачено(месяц): {total_income} $\n" \
           f"├Всего профита(месяц): {total_profit} $\n" \
           f"├Использование GPT3(месяц): {total_use_gpt3}\n" \
           f"├Использование GPT4(месяц): {total_use_gpt4}\n" \
           f"├Использование FREE API: {total_use_free_api}\n" \
           f"├Задано в этом месяце: {count_questions} вопросов.\n" \
           f"└Заблокированных: {total_blocked} чел.\n"
    return info

def finance_calculator():
    query = f"SELECT spending, model, free_api FROM history_question_answer_admin WHERE TO_CHAR(date_time, 'YYYY-MM') = TO_CHAR(NOW(), 'YYYY-MM') AND question IS NOT NULL;"
    cursor.execute(query)
    results = cursor.fetchall()
    cours = db_get(f'SELECT cours_currency FROM settings;').split('-')
    total_profit = 0
    total_income = 0
    total_use_gpt4 = 0
    total_use_gpt3 = 0
    total_use_free_api = 0
    for result in results:
        if result[0] != None:
            spending = result[0].split('~')
            if result[0] != '-':
                spend = float(spending[3])
                currency = spending[5]
                model = result[1]
                free_api = result[2]
                if free_api:
                    if currency == '₽':
                        total_profit += spend / float(cours[0])
                    elif currency == '₸':
                        total_profit += spend / float(cours[1])
                    elif currency == '₴':
                        total_profit += spend / float(cours[2])
                        total_profit += spend
                    total_use_free_api += 1
                else:
                    if currency == '₽':
                        total_profit += (spend / float(cours[0])) * 0.1
                        total_income += (spend / float(cours[0]))
                    elif currency == '₸':
                        total_profit += (spend / float(cours[1])) * 0.1
                        total_income += (spend / float(cours[1]))
                    elif currency == '₴':
                        total_profit += (spend / float(cours[2])) * 0.1
                        total_income += (spend / float(cours[2]))
                    else:
                        total_profit += spend * 0.1
                        total_income += spend
                if model == 'gpt-4-vision-preview':
                    total_use_gpt4 += 1
                else:
                    total_use_gpt3 += 1
    return round(total_income, 5), round(total_profit, 5), total_use_gpt3, total_use_gpt4, total_use_free_api

def add_balance_user(message, message_menu):
    info = message.text.split('-')
    user_id = info[0]
    try:
        balance = db_get(f"SELECT balance FROM users WHERE user_id = {user_id}")
        country = db_get(f"SELECT country FROM users WHERE user_id = {user_id}")
        if country == 'Россия':
            currency = 'RUB'
        elif country == 'Казахстан':
            currency = 'KZT'
        elif country == 'Украина':
            currency = 'UAH'
        else:
            currency = 'USD'
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        count_messages = float(info[1]) + float(balance)
        db_set(f"UPDATE users SET balance = {count_messages} WHERE user_id = {user_id}")
        bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id,
                              text=f"Успешно! \nПользователю {user_id} добавлено {info[1]} {currency}.\nИтоговое количество {count_messages} {currency}",
                              reply_markup=admin_back)
        db_insert_transactions(user_id, 7, None, float(info[1]), currency, True, time_now, None, None, None)
    except:
        bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id,
                              text="Ошибка! Пользователя не существует!", reply_markup=admin_back)
    try:
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    except:
        pass

def set_new_status(message, message_menu):
    if int(message.text) == 1:
        status_bd = True
        status = "работает"
    else:
        status_bd = False
        status = "отключен"
    db_set(f"UPDATE settings SET status = {status_bd}")
    try:
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    except:
        pass
    bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id,
                          text=f"Успешно!\nБот {status} для пользователей", reply_markup=admin_back)

def set_new_tokens(message, message_menu):
    db_set(f"UPDATE settings SET tokens = {message.text}")
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id, text="Успешно!",
                          reply_markup=admin_back)

def set_new_temp(message, message_menu):
    db_set(f"UPDATE settings SET temperature = {message.text}")
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id, text="Успешно!",
                          reply_markup=admin_back)

def set_new_referal_bonus(message, message_menu):
    db_set(f"UPDATE settings SET referal_bonus = '{message.text}'")
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id, text="Успешно!",
                          reply_markup=admin_back)

def set_new_reffer_bonus(message, message_menu):
    db_set(f"UPDATE settings SET reffer_bonus = '{message.text}'")
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id, text="Успешно!",
                          reply_markup=admin_back)

def set_new_trial_bonus(message, message_menu):
    db_set(f"UPDATE settings SET trial_bonus = '{message.text}'")
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id, text="Успешно!",
                          reply_markup=admin_back)

def set_new_gpt4_price(message, message_menu):
    db_set(f"UPDATE settings SET gpt4 = '{message.text}'")
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id, text="Успешно!",
                          reply_markup=admin_back)

def set_new_gpt3_price(message, message_menu):
    db_set(f"UPDATE settings SET gpt3 = '{message.text}'")
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id, text="Успешно!",
                          reply_markup=admin_back)

def set_new_whisper_price(message, message_menu):
    db_set(f"UPDATE settings SET whisper = '{message.text}'")
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id, text="Успешно!",
                          reply_markup=admin_back)

def set_new_cashback(message, message_menu):
    db_set(f"UPDATE settings SET cashback = {message.text}")
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id, text="Успешно!",
                          reply_markup=admin_back)

def set_on_off_free_api(message, message_menu):
    if message.text == '1':
        status = True
    else:
        status = False
    db_set(f"UPDATE settings SET free_api = {status}")
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id, text="Успешно!",
                          reply_markup=admin_back)

def all_message(message, message_menu):
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    a = 0
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id,
                          text=f"⌛Отправляю сообщения...",
                          reply_markup=admin_back)
    close_msg = get_interface(message.from_user.id, 'close_msg')
    for user in users:
        try:
            bot.send_message(user[0], text=message.text, parse_mode='Markdown', reply_markup=close_msg)
        except:
            a += 1
    db_set(f"UPDATE settings SET total_blocked = {a}")

    bot.edit_message_text(chat_id=message_menu.chat.id, message_id=message_menu.id,
                          text=f"Успешно!\nСообщение отправлено пользователям!\nКоличество заблокированных: {a}",
                          reply_markup=admin_back)

def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(chat_id=f'@{channel_username}', user_id=user_id)
        if member and (member.status == 'creator' or member.status == 'administrator' or member.status == 'member'):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def markdown_escape(text):
    """Escape special characters in a string for use in Telegram Markdown"""
    escape_chars = '_*['
    escaped_text = ''
    in_code_block = False
    for i, char in enumerate(text):
        if char == '`':
            # toggle in_code_block flag when encountering backticks
            in_code_block = not in_code_block
            escaped_text += char
        elif char in escape_chars and not in_code_block:
            escaped_text += '\\' + char
        else:
            escaped_text += char
    # if the last character is a backtick and in_code_block is True, add a closing backtick
    if text[-1] == '`' and in_code_block:
        escaped_text += '`'
    # if in_code_block is still True, add a closing backtick
    if in_code_block:
        escaped_text += '```'
    return escaped_text

def add_trial_bonus(user_id):
    db_results = db_all_get(f"SELECT * FROM users WHERE user_id = {user_id}")
    balance = db_results[9]
    country = db_results[11]
    bonus_info = db_get(f"SELECT trial_bonus FROM settings").split('-')
    if country == 'Россия':
        bonus = float(bonus_info[0])
        currency = 'RUB'
    elif country == 'Казахстан':
        bonus = float(bonus_info[1])
        currency = 'KZT'
    elif country == 'Украина':
        bonus = float(bonus_info[2])
        currency = 'UAH'
    else:
        bonus = float(bonus_info[3])
        currency = 'USD'
    if bonus == 0:
        return
    new_balance_bonus = float(balance) + bonus
    db_set(f"UPDATE users SET balance = {new_balance_bonus} WHERE user_id = {user_id}")
    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db_insert_transactions(user_id, 7, None, bonus, currency, True, time_now, None, None, None)

def get_chat_price(id_chat, user_id):
    cursor.execute(f"SELECT spending FROM history_question_answer WHERE id_chat = {id_chat} AND user_id = {user_id}")
    spending_list = cursor.fetchall()
    total_chat_price = 0
    for spending in spending_list:
        if spending[0] != "-":
            total_chat_price += float(spending[0].split("~")[3])
    return total_chat_price

def voice_convert_ogg(user_id, file_id):
    messages_path_mp3 = os.path.join(f'{MESSAGES_DIR}/{user_id}/', f'{file_id}.mp3')
    messages_path_ogg = os.path.join(f'{MESSAGES_DIR}/{user_id}/', f'{file_id}.ogg')
    command = f'ffmpeg\\bin\\ffmpeg.exe -i {messages_path_mp3} -c:a libopus -b:a 192k {messages_path_ogg}'
    subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return messages_path_ogg, messages_path_mp3

def voice_convert(user_id, file_id):
    messages_path_ogg = os.path.join(f'{MESSAGES_DIR}/{user_id}/', f'{file_id}.ogg')
    messages_path_mp3 = os.path.join(f'{MESSAGES_DIR}/{user_id}/', f'{file_id}.mp3')
    command = f'ffmpeg\\bin\\ffmpeg.exe -i {messages_path_ogg} -vn -ar 44100 -ac 2 -ab 192k -f mp3 {messages_path_mp3}'
    subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(messages_path_ogg)

def voice_create(user_id, answer):
    price_tts = float(db_get('SELECT tts FROM settings;'))
    voice = db_get(f"SELECT ai_voice FROM users WHERE user_id = {user_id}")
    price = (len(answer) / 1000) * price_tts
    if len(answer) > 4096:
        return None, 0
    else:
        name = f"{user_id}-{random.randint(10000, 10000000)}"
        messages_path_ogg = os.path.join(f'{MESSAGES_DIR}/{user_id}/', f'{name}.mp3')
        openai.base_url = paid_api
        openai.api_key = token
        response = openai.audio.speech.create(model="tts-1-hd",
                                              voice=voice,
                                              input=answer)
        response.stream_to_file(messages_path_ogg)
        path_file, path_file_mp3 = voice_convert_ogg(user_id, name)
        balance, rashod = balance_out(price, user_id)
        rashod = round(rashod, 3)
        return path_file, rashod, path_file_mp3

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def audio_to_base64(audio_path):
    with open(audio_path, "rb") as audio_file:
        return base64.b64encode(audio_file.read()).decode("utf-8")

# декоратор старта(функция при запуске бота пользователем)
@bot.message_handler(commands=['start'])
def send_welcome(message: types.Message):
    if db_check_exist(message.from_user.id) == []:
        user_id = message.from_user.id
        referrer = 0
        date_reg = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        os.makedirs(f'{MESSAGES_DIR}/{message.chat.id}/', exist_ok=True)
        messages_path = os.path.join(f'{MESSAGES_DIR}/{message.chat.id}/', f"{message.chat.id}.txt")
        if not os.path.exists(messages_path):
            open(messages_path, 'w').close()
        # Проверяем наличие хоть какой-то дополнительной информации из ссылки
        if " " in message.text:
            referrer_candidate = message.text.split()[1]
            # Пробуем преобразовать строку в число
            try:
                referrer_candidate = int(referrer_candidate)
                # Проверяем на несоответствие TG ID пользователя TG ID реферера
                # Также проверяем, есть ли такой реферер в базе данных
                if user_id != referrer_candidate and db_check_exist(referrer_candidate) != []:
                    referrer = referrer_candidate
                    db_insert_users(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                                    message.from_user.username, referrer, date_reg)
                    language = db_get(f"SELECT language FROM users WHERE user_id = {referrer}")
                    refferer_bonus = add_bonus("reffer", referrer, date_reg, user_id)
                    if language == "Русский":
                        bot.send_message(referrer,
                                         text=f"Вам начислено {refferer_bonus} баллов за "
                                              f"приглашенного человека({message.from_user.first_name}).",
                                         reply_markup=get_interface(referrer, 'close_msg'))
                    if language == "Казахский":
                        bot.send_message(referrer,
                                         text=f"Шақырылған адамға {refferer_bonus} балдар беріледі({message.from_user.first_name}).",
                                         reply_markup=get_interface(referrer, 'close_msg'))
                    if language == "Украинский":
                        bot.send_message(referrer,
                                         text=f"Вам нараховано {refferer_bonus} балів за запрошеної особи({message.from_user.first_name}).",
                                         reply_markup=get_interface(referrer, 'close_msg'))
                    if language == "Английский":
                        bot.send_message(referrer,
                                         text=f"You are awarded {refferer_bonus} points for the invited person({message.from_user.first_name}).",
                                         reply_markup=get_interface(referrer, 'close_msg'))
            except ValueError:
                pass
        else:
            db_insert_users(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                            message.from_user.username, referrer, date_reg)
    db_results = db_all_get(f"SELECT * FROM users WHERE user_id = {message.chat.id}")
    country = db_results[11]
    language = db_results[10]
    terms = db_results[6]
    if language != None:
        if country != None:
            if is_user_in_channel(message.chat.id):
                if terms:
                    bot.send_message(message.chat.id,
                                     text=get_interface(message.from_user.id, "welcome_text"),
                                     parse_mode='Markdown',
                                     reply_markup=get_interface(message.from_user.id, 'welcome'))
                else:
                    if country == "Казахстан":
                        politika = ''
                        if language == 'Русский':
                            politika = f"8. Вы соглашаетесь с условиями [Политики конфеденциальности и Договором публичной оферты на предоставление услуг]({politika_confedence})"
                        elif language == 'Казахский':
                            politika = f"8. Сіз [Құпиялық саясатының және қызметтерді көрсетуге арналған Қоғамдық ұсыныс келісімінің шарттарымен келісесіз]({politika_confedence})"
                        bot.send_message(message.chat.id,
                                         text=f'{get_interface(message.from_user.id, "terms_text")}\n{politika}',
                                         parse_mode='Markdown',
                                         reply_markup=get_interface(message.from_user.id, 'terms_markup'))
                    else:
                        bot.send_message(message.chat.id, text=get_interface(message.from_user.id, 'terms_text'),
                                         parse_mode='Markdown',
                                         reply_markup=get_interface(message.from_user.id, 'terms_markup'))
            else:
                bot.send_message(message.chat.id,
                                 text=get_interface(message.from_user.id, 'subscribe_invite'), parse_mode='Markdown',
                                 reply_markup=get_interface(message.from_user.id, 'subscribe_menu'))
        else:
            bot.send_message(message.chat.id,
                             text=choose_country_text, parse_mode='Markdown', reply_markup=choose_country)
    else:
        bot.send_message(message.chat.id,
                         text=choose_lanuage_text, parse_mode='Markdown', reply_markup=choose_lanuage)

# декоратор голосовых сообщений(функция обрабатывающая голосовые сообщения)
@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    global msg2, voice_user, voice_bot
    msg2 = 1
    voice_user = None
    voice_bot = None
    openai.api_key = token
    openai.base_url = paid_api
    db_results = db_all_get(f"SELECT * FROM users WHERE user_id = {message.chat.id}")
    country = db_results[11]
    language = db_results[10]
    terms = db_results[6]
    if language != None:
        if country != None:
            if is_user_in_channel(message.chat.id):
                if terms:
                    if db_get(f"SELECT status FROM settings"):
                        db_results = db_all_get(f"SELECT * FROM users WHERE user_id = {message.from_user.id}")
                        balance = db_results[9]
                        country = db_results[11]
                        status_chat = db_results[7]
                        if status_chat:
                            time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            msg = bot.send_message(message.chat.id,
                                                   get_interface(message.from_user.id, "recognize_voice"))
                            voice_info = message.voice
                            file_id = voice_info.file_id
                            file_path = bot.get_file(file_id).file_path
                            # Скачиваем файл на сервер
                            downloaded_file = bot.download_file(file_path)
                            # Сохраняем файл на диск в формате .ogg
                            messages_path = os.path.join(f'{MESSAGES_DIR}/{message.chat.id}/', f'{file_id}.ogg')
                            with open(messages_path, 'wb') as new_file:
                                new_file.write(downloaded_file)
                            new_file.close()
                            voice_convert(message.chat.id, file_id)
                            file = os.path.join(f'{MESSAGES_DIR}/{message.chat.id}/', f'{file_id}.mp3')
                            f = MP3(file)
                            price_voice_admin = float(db_get(f"SELECT whisper FROM settings"))
                            price_voice = round(price_voice_admin * (f.info.length / 60), 5)
                            cours_currency = db_get(f"SELECT cours_currency FROM settings").split('-')
                            if country == "Россия":
                                cours = cours_currency[0]
                            elif country == "Казахстан":
                                cours = cours_currency[1]
                            elif country == "Украина":
                                cours = cours_currency[2]
                            else:
                                cours = cours_currency[3]
                            if price_voice > float(balance) / float(cours):
                                bot.delete_message(message.chat.id, message.message_id)
                                bot.delete_message(msg.chat.id, msg.message_id)
                                msg2 = bot.send_message(message.chat.id,
                                                        get_interface(message.from_user.id, 'insufficient_funds'),
                                                        reply_markup=get_interface(message.from_user.id,
                                                                                   'chat_settings'))
                                db_insert_aaq(message.from_user.id, "ERROR", "ERROR",
                                              f"{msg.message_id}-{msg2.message_id}", time_now, info_spending="-",
                                              model='gpt-4', free_api=False)
                                return
                            no_balance, price_voice = balance_out(price_voice, message.chat.id)
                            price_voice = round(price_voice, 4)
                            audio_file = open(file, "rb")
                            transcript = openai.audio.transcriptions.create(model="whisper-1", file=audio_file).text
                            audio_file.close()
                            if transcript != "":
                                voice_msg = get_interface(message.from_user.id, "voice_message")
                                user_id = message.from_user.id
                                user_name = message.from_user.first_name
                                username = message.from_user.username
                                messages = get_messages(message.from_user.id)
                                msg = bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                                            text=f'{get_interface(message.from_user.id, "wait_msg")}\n{voice_msg}\n{transcript}')
                                messages.append(create_message("user", transcript))
                                bot.send_chat_action(message.chat.id, 'typing')
                                print('Генерация ответа...')
                                status, answer, info, free_api = get_ai_answer(messages, user_id)
                                total_tokens = float(info.split('~')[0]) + float(info.split('~')[1])
                                total_price = round(float(info.split('~')[2]), 5)
                                balance = info.split('~')[3]
                                if country == "Россия":
                                    currency = "₽"
                                elif country == "Казахстан":
                                    currency = "₸"
                                elif country == "Украина":
                                    currency = "₴"
                                else:
                                    currency = "$"
                                model = info.split('~')[4]
                                voice_user = file
                                if status:
                                    messages.append(create_message("assistant", answer))
                                    set_messages(message.from_user.id, messages)
                                    print(f"{model} Free API: {free_api} ID: " + str(
                                        user_id) + " Имя пользователя: " + str(
                                        user_name) + " Логин пользователя: " + str(username) +
                                          " Вопрос пользователя: \n" + voice_msg + str(
                                        transcript) + "\n_______________________________")
                                    if db_results[14]:
                                        path, price_voice2, file_mp3 = voice_create(user_id, answer)
                                        voice_bot = file_mp3
                                        total_price2 = round(price_voice + total_price + price_voice2, 5)
                                        info_spending = f"{price_voice}~{total_tokens}~{total_price}~{total_price2}~{balance}~{currency}~{price_voice2}~0"
                                        info = get_interface(user_id, "rashod").replace("0", "{}").format(price_voice,
                                                                                                          price_voice2,
                                                                                                          total_tokens,
                                                                                                          total_price,
                                                                                                          total_price2,
                                                                                                          balance)
                                        if path == None:
                                            try:
                                                bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                                                      text=markdown_escape(answer) + info,
                                                                      parse_mode='Markdown',
                                                                      reply_markup=get_interface(message.from_user.id,
                                                                                                 'chat_settings'))
                                            except Exception as e:
                                                print(str(e))
                                                print('parse_error')
                                                bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                                                      text=answer + info,
                                                                      reply_markup=get_interface(message.from_user.id,
                                                                                                 'chat_settings'))
                                        else:
                                            bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
                                            msg = bot.send_voice(message.chat.id, voice=open(path, 'rb'))
                                            print('Использовано озвучивание')
                                            msg2 = bot.send_message(message.chat.id, text=info,
                                                                    reply_markup=get_interface(message.from_user.id,
                                                                                               'chat_settings'))
                                            msg2 = msg2.message_id
                                    else:
                                        total_price2 = round(price_voice + total_price, 5)
                                        info_spending = f"{price_voice}~{total_tokens}~{total_price}~{total_price2}~{balance}~{currency}~0~0"
                                        info = get_interface(user_id, "rashod").replace("0", "{}").format(price_voice,
                                                                                                          0,
                                                                                                          total_tokens,
                                                                                                          total_price,
                                                                                                          total_price2,
                                                                                                          balance)
                                        try:
                                            bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                                                  text=markdown_escape(answer) + info,
                                                                  parse_mode='Markdown',
                                                                  reply_markup=get_interface(message.from_user.id,
                                                                                             'chat_settings'))
                                        except Exception as e:
                                            print(str(e))
                                            print('parse_error')
                                            bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                                                  text=answer + info,
                                                                  reply_markup=get_interface(message.from_user.id,
                                                                                             'chat_settings'))
                                    db_insert_aaq(message.from_user.id, f'{voice_msg}\n{transcript}', answer,
                                                  f"{msg.message_id}-{message.message_id}-{msg2}",
                                                  time_now, info_spending, model, free_api, None, voice_user, None,
                                                  voice_bot)
                                else:
                                    bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=answer,
                                                          reply_markup=get_interface(message.from_user.id,
                                                                                     'chat_settings'))
                                    db_insert_aaq(message.from_user.id, "ERROR", "ERROR",
                                                  f"{msg.message_id}-{message.message_id}-{msg2}", time_now,
                                                  info_spending="-", model=model, free_api=False)
                            else:
                                bot.send_message(message.chat.id, get_interface(message.from_user.id, 'empty_voice'),
                                                 reply_markup=get_interface(message.from_user.id, 'close_msg'))
                        else:
                            bot.delete_message(message.chat.id, message.message_id)
                            bot.send_message(message.chat.id, get_interface(message.from_user.id, 'error_text_msg'),
                                             reply_markup=get_interface(message.from_user.id, 'welcome'))
                    else:
                        bot.delete_message(message.chat.id, message.message_id)
                        bot.send_message(message.chat.id, get_interface(message.from_user.id, 'bot_out'))
                else:
                    if country == "Казахстан":
                        politika = ''
                        if language == 'Русский':
                            politika = f"8. Вы соглашаетесь с условиями [Политики конфеденциальности и Договором публичной оферты на предоставление услуг]({politika_confedence})"
                        elif language == 'Казахский':
                            politika = f"8. Сіз [Құпиялық саясатының және қызметтерді көрсетуге арналған Қоғамдық ұсыныс келісімінің шарттарымен келісесіз]({politika_confedence})"
                        bot.delete_message(message.chat.id, message.message_id)
                        bot.send_message(message.chat.id,
                                         text=f'{get_interface(message.from_user.id, "terms_text")}\n{politika}',
                                         parse_mode='Markdown',
                                         reply_markup=get_interface(message.from_user.id, 'terms_markup'))
                    else:
                        bot.delete_message(message.chat.id, message.message_id)
                        bot.send_message(message.chat.id, text=get_interface(message.from_user.id, 'terms_text'),
                                         parse_mode='Markdown',
                                         reply_markup=get_interface(message.from_user.id, 'terms_markup'))
            else:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id,
                                 text=get_interface(message.from_user.id, 'subscribe_invite'), parse_mode='Markdown',
                                 reply_markup=get_interface(message.from_user.id, 'subscribe_warning'))
        else:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id,
                             text=choose_country_text, parse_mode='Markdown', reply_markup=choose_country)
    else:
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id,
                         text=choose_lanuage_text, parse_mode='Markdown', reply_markup=choose_lanuage)

# декоратор текстовых сообщения(функция обрабатывающая текстовые сообщения)
@bot.message_handler(content_types=['text'])
def text(message):
    global msg2, voice_file
    msg2 = 1
    voice_file = None
    db_results = db_all_get(f"SELECT * FROM users WHERE user_id = {message.chat.id}")
    country = db_results[11]
    language = db_results[10]
    terms = db_results[6]
    if language != None:
        if country != None:
            if is_user_in_channel(message.chat.id):
                if terms:
                    if message.text.startswith('!'):
                        question = message.text.replace("!", "").strip()
                        if db_get(f"SELECT status FROM settings"):
                            db_results = db_all_get(f"SELECT * FROM users WHERE user_id = {message.from_user.id}")
                            country = db_results[11]
                            status_chat = db_results[7]
                            if status_chat:
                                time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                user_id = message.from_user.id
                                user_name = message.from_user.first_name
                                username = message.from_user.username
                                messages = get_messages(message.from_user.id)
                                msg = bot.send_message(message.chat.id, get_interface(message.from_user.id, 'wait_msg'))
                                messages.append(create_message("user", question))
                                bot.send_chat_action(message.chat.id, 'typing')
                                print('Генерация ответа...')
                                status, answer, info, free_api = get_ai_answer(messages, user_id)
                                if status:
                                    total_tokens = float(info.split('~')[0]) + float(info.split('~')[1])
                                    total_price = round(float(info.split('~')[2]), 5)
                                    balance = info.split('~')[3]
                                    if country == "Россия":
                                        currency = "₽"
                                    elif country == "Казахстан":
                                        currency = "₸"
                                    elif country == "Украина":
                                        currency = "₴"
                                    else:
                                        currency = "$"
                                    model_api = info.split('~')[4]
                                    messages.append(create_message("assistant", answer))
                                    set_messages(message.from_user.id, messages)
                                    print(f"{model_api} Free API: {free_api} ID: " + str(user_id) + " Имя пользователя: " + str(
                                        user_name) + " Логин пользователя: " + str(username) +
                                          " Вопрос пользователя: \n" + str(
                                        question) + "\n_______________________________")
                                    if db_results[14]:
                                        path, price_voice2, file_mp3 = voice_create(user_id, answer)
                                        voice_file = file_mp3
                                        total_price2 = round(total_price + price_voice2, 5)
                                        info_spending = f"0~{total_tokens}~{total_price}~{total_price2}~{balance}~{currency}~{price_voice2}~0"
                                        info = get_interface(user_id, "rashod").replace("0", "{}").format(0,
                                                                                                          price_voice2,
                                                                                                          total_tokens,
                                                                                                          total_price,
                                                                                                          total_price2,
                                                                                                          balance)
                                        if path == None:
                                            try:
                                                bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                                                      text=markdown_escape(answer) + info,
                                                                      parse_mode='Markdown',
                                                                      reply_markup=get_interface(message.from_user.id,
                                                                                                 'chat_settings'))
                                            except Exception as e:
                                                print(str(e))
                                                print('parse_error')
                                                bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                                                      text=answer + info,
                                                                      reply_markup=get_interface(message.from_user.id,
                                                                                                 'chat_settings'))
                                        else:
                                            bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
                                            print('Использовано озвучивание')
                                            msg = bot.send_voice(message.chat.id, voice=open(path, 'rb'))
                                            msg2 = bot.send_message(message.chat.id, text=info,
                                                                    reply_markup=get_interface(message.from_user.id,
                                                                                               'chat_settings'))
                                            msg2 = msg2.message_id
                                    else:
                                        info_spending = f"0~{total_tokens}~{total_price}~{total_price}~{balance}~{currency}~0~0"
                                        info = get_interface(user_id, "rashod").replace("0", "{}").format(0,
                                                                                                          0,
                                                                                                          total_tokens,
                                                                                                          total_price,
                                                                                                          total_price,
                                                                                                          balance)
                                        try:
                                            bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                                                  text=markdown_escape(answer) + info,
                                                                  parse_mode='Markdown',
                                                                  reply_markup=get_interface(message.from_user.id,
                                                                                             'chat_settings'))
                                        except Exception as e:
                                            print(str(e))
                                            print('parse_error')
                                            bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                                                  text=answer + info,
                                                                  reply_markup=get_interface(message.from_user.id,
                                                                                             'chat_settings'))
                                    db_insert_aaq(message.from_user.id, question, answer,
                                                  f"{msg.message_id}-{message.message_id}-{msg2}",
                                                  time_now, info_spending, model_api, free_api, None, None, None,
                                                  voice_file)
                                else:
                                    bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=answer,
                                                          reply_markup=get_interface(message.from_user.id,
                                                                                     'chat_settings'))
                                    db_insert_aaq(message.from_user.id, "ERROR", "ERROR",
                                                  f"{msg.message_id}-{message.message_id}-{msg2}", time_now,
                                                  info_spending="-", model='gpt-3.5-turbo', free_api=False)
                            else:
                                bot.delete_message(message.chat.id, message.message_id)
                                bot.send_message(message.chat.id, get_interface(message.from_user.id, 'error_text_msg'),
                                                 reply_markup=get_interface(message.from_user.id, 'welcome'))
                        else:
                            bot.delete_message(message.chat.id, message.message_id)
                            bot.send_message(message.chat.id, get_interface(message.from_user.id, 'bot_out'))
                    elif message.text == password_admin and message.chat.id == ADMIN_ID:
                        info = create_info_adminmenu()
                        bot.send_message(message.chat.id, text=info, reply_markup=admin_menu)
                    else:
                        bot.delete_message(message.chat.id, message.message_id)
                        bot.send_message(message.chat.id, text=get_interface(message.chat.id, "instruction_text"),
                                         parse_mode='Markdown',
                                         reply_markup=get_interface(message.chat.id, 'close_msg'))
                else:
                    if country == "Казахстан":
                        politika = ''
                        if language == 'Русский':
                            politika = f"8. Вы соглашаетесь с условиями [Политики конфеденциальности и Договором публичной оферты на предоставление услуг]({politika_confedence})"
                        elif language == 'Казахский':
                            politika = f"8. Сіз [Құпиялық саясатының және қызметтерді көрсетуге арналған Қоғамдық ұсыныс келісімінің шарттарымен келісесіз]({politika_confedence})"
                        bot.delete_message(message.chat.id, message.message_id)
                        bot.send_message(message.chat.id,
                                         text=f'{get_interface(message.from_user.id, "terms_text")}\n{politika}',
                                         parse_mode='Markdown',
                                         reply_markup=get_interface(message.from_user.id, 'terms_markup'))
                    else:
                        bot.delete_message(message.chat.id, message.message_id)
                        bot.send_message(message.chat.id, text=get_interface(message.from_user.id, 'terms_text'),
                                         parse_mode='Markdown',
                                         reply_markup=get_interface(message.from_user.id, 'terms_markup'))
            else:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id,
                                 text=get_interface(message.from_user.id, 'subscribe_invite'), parse_mode='Markdown',
                                 reply_markup=get_interface(message.from_user.id, 'subscribe_warning'))
        else:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id,
                             text=choose_country_text, parse_mode='Markdown', reply_markup=choose_country)
    else:
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id,
                         text=choose_lanuage_text, parse_mode='Markdown', reply_markup=choose_lanuage)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    global msg2
    msg2 = 1
    db_results = db_all_get(f"SELECT * FROM users WHERE user_id = {message.chat.id}")
    country = db_results[11]
    language = db_results[10]
    terms = db_results[6]
    if language != None:
        if country != None:
            if is_user_in_channel(message.chat.id):
                if terms:
                    if message.caption != None:
                        if message.caption.startswith('!'):
                            question = message.caption.replace("!", "").strip()
                            if db_get(f"SELECT status FROM settings"):
                                db_results = db_all_get(f"SELECT * FROM users WHERE user_id = {message.from_user.id}")
                                country = db_results[11]
                                status_chat = db_results[7]
                                model = db_results[12]
                                if model != 'gpt-4-vision-preview':
                                    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                                    bot.send_message(chat_id=message.chat.id,
                                                     text=get_interface(message.chat.id, 'photo_gpt'),
                                                     reply_markup=get_interface(message.chat.id, 'close_msg'))
                                    return
                                if status_chat:
                                    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    user_id = message.from_user.id
                                    user_name = message.from_user.first_name
                                    username = message.from_user.username
                                    messages = get_messages(message.from_user.id)
                                    msg = bot.send_message(message.chat.id, get_interface(message.from_user.id, 'wait_msg'))
                                    bot.send_chat_action(message.chat.id, 'typing')
                                    file_id = message.photo[-1].file_id
                                    file_info = bot.get_file(file_id)
                                    download_url = f'https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}'
                                    messages_path = os.path.join(f'{MESSAGES_DIR}/{message.chat.id}/',
                                                                 f"photo_{file_id}.jpg")
                                    response = requests.get(download_url)
                                    if response.status_code == 200:
                                        with open(messages_path, 'wb') as file:
                                            file.write(response.content)
                                    photo_user = image_to_base64(messages_path)
                                    photo_user2 = messages_path
                                    messages.append(create_message("user", question, photo_user))
                                    print('Генерация ответа...')
                                    status, answer, info, free_api = get_ai_answer(messages, user_id)
                                    if status:
                                        total_tokens = float(info.split('~')[0]) + float(info.split('~')[1])
                                        total_price = round(float(info.split('~')[2]), 5)
                                        balance = info.split('~')[3]
                                        if country == "Россия":
                                            currency = "₽"
                                        elif country == "Казахстан":
                                            currency = "₸"
                                        elif country == "Украина":
                                            currency = "₴"
                                        else:
                                            currency = "$"
                                        model_api = info.split('~')[4]
                                        messages.append(create_message("assistant", answer))
                                        set_messages(message.from_user.id, messages)
                                        print(f"ФОТО {model_api} Free API: {free_api} ID: " + str(
                                            user_id) + " Имя пользователя: " + str(
                                            user_name) + " Логин пользователя: " + str(username) +
                                              " Вопрос пользователя: \n" + str(
                                            question) + "\n_______________________________")
                                        voice_bot = None
                                        if db_results[14]:
                                            path, price_voice2, file_mp3 = voice_create(user_id, answer)
                                            voice_bot = file_mp3
                                            total_price2 = round(total_price + price_voice2, 5)
                                            info_spending = f"0~{total_tokens}~{total_price}~{total_price2}~{balance}~{currency}~{price_voice2}~0"
                                            info = get_interface(user_id, "rashod").replace("0", "{}").format(0,
                                                                                                              price_voice2,
                                                                                                              total_tokens,
                                                                                                              total_price,
                                                                                                              total_price2,
                                                                                                              balance)
                                            if path == None:
                                                try:
                                                    bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                                                          text=markdown_escape(answer) + info,
                                                                          parse_mode='Markdown',
                                                                          reply_markup=get_interface(message.from_user.id,
                                                                                                     'chat_settings'))
                                                except Exception as e:
                                                    print(str(e))
                                                    print('parse_error')
                                                    bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                                                          text=answer + info,
                                                                          reply_markup=get_interface(message.from_user.id,
                                                                                                     'chat_settings'))
                                            else:
                                                print('Использовано озвучивание')
                                                bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
                                                msg = bot.send_voice(message.chat.id, voice=open(path, 'rb'))
                                                msg2 = bot.send_message(message.chat.id, text=info,
                                                                        reply_markup=get_interface(message.from_user.id,
                                                                                                   'chat_settings'))
                                                msg2 = msg2.message_id
                                        else:
                                            info_spending = f"0~{total_tokens}~{total_price}~{total_price}~{balance}~{currency}~0~0"
                                            info = get_interface(user_id, "rashod").replace("0", "{}").format(0,
                                                                                                              0,
                                                                                                              total_tokens,
                                                                                                              total_price,
                                                                                                              total_price,
                                                                                                              balance)
                                            try:
                                                bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                                                      text=markdown_escape(answer) + info,
                                                                      parse_mode='Markdown',
                                                                      reply_markup=get_interface(message.from_user.id,
                                                                                                 'chat_settings'))
                                            except Exception as e:
                                                print(str(e))
                                                print('parse_error')
                                                bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                                                      text=answer + info,
                                                                      reply_markup=get_interface(message.from_user.id,
                                                                                                 'chat_settings'))
                                        db_insert_aaq(message.from_user.id, question, answer,
                                                      f"{msg.message_id}-{message.message_id}-{msg2}", time_now,
                                                      info_spending, model_api, free_api, photo_user2, None, None,
                                                      voice_bot)
                                    else:
                                        bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=answer,
                                                              reply_markup=get_interface(message.from_user.id,
                                                                                         'chat_settings'))
                                        db_insert_aaq(message.from_user.id, "ERROR", "ERROR",
                                                      f"{msg.message_id}-{message.message_id}-{msg2}", time_now,
                                                      info_spending="-", model='gpt-3.5-turbo', free_api=False)
                                else:
                                    bot.delete_message(message.chat.id, message.message_id)
                                    bot.send_message(message.chat.id, get_interface(message.from_user.id, 'error_text_msg'),
                                                     reply_markup=get_interface(message.from_user.id, 'welcome'))
                            else:
                                bot.delete_message(message.chat.id, message.message_id)
                                bot.send_message(message.chat.id, get_interface(message.from_user.id, 'bot_out'))
                        else:
                            bot.delete_message(message.chat.id, message.message_id)
                            bot.send_message(message.chat.id, text=get_interface(message.chat.id, "instruction_text"),
                                             parse_mode='Markdown',
                                             reply_markup=get_interface(message.chat.id, 'close_msg'))
                    else:
                        bot.delete_message(message.chat.id, message.message_id)
                        bot.send_message(message.chat.id, text=get_interface(message.chat.id, "instruction_text"),
                                         parse_mode='Markdown',
                                         reply_markup=get_interface(message.chat.id, 'close_msg'))
                else:
                    if country == "Казахстан":
                        politika = ''
                        if language == 'Русский':
                            politika = f"8. Вы соглашаетесь с условиями [Политики конфеденциальности и Договором публичной оферты на предоставление услуг]({politika_confedence})"
                        elif language == 'Казахский':
                            politika = f"8. Сіз [Құпиялық саясатының және қызметтерді көрсетуге арналған Қоғамдық ұсыныс келісімінің шарттарымен келісесіз]({politika_confedence})"
                        bot.delete_message(message.chat.id, message.message_id)
                        bot.send_message(message.chat.id,
                                         text=f'{get_interface(message.from_user.id, "terms_text")}\n{politika}',
                                         parse_mode='Markdown',
                                         reply_markup=get_interface(message.from_user.id, 'terms_markup'))
                    else:
                        bot.delete_message(message.chat.id, message.message_id)
                        bot.send_message(message.chat.id, text=get_interface(message.from_user.id, 'terms_text'),
                                         parse_mode='Markdown',
                                         reply_markup=get_interface(message.from_user.id, 'terms_markup'))
            else:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id,
                                 text=get_interface(message.from_user.id, 'subscribe_invite'), parse_mode='Markdown',
                                 reply_markup=get_interface(message.from_user.id, 'subscribe_warning'))
        else:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id,
                             text=choose_country_text, parse_mode='Markdown', reply_markup=choose_country)
    else:
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id,
                         text=choose_lanuage_text, parse_mode='Markdown', reply_markup=choose_lanuage)

# декоратор кнопок(функции обрабатывающая нажатия кнопок)
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == 'russian_language':
            db_set(f"UPDATE users SET language = 'Русский' WHERE user_id = {call.message.chat.id}")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=choose_country_text, parse_mode='Markdown', reply_markup=choose_country)
        if call.data == 'kazakh_language':
            db_set(f"UPDATE users SET language = 'Казахский' WHERE user_id = {call.message.chat.id}")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=choose_country_text, parse_mode='Markdown', reply_markup=choose_country)
        if call.data == 'ukrain_language':
            db_set(f"UPDATE users SET language = 'Украинский' WHERE user_id = {call.message.chat.id}")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=choose_country_text, parse_mode='Markdown', reply_markup=choose_country)
        if call.data == 'english_language':
            db_set(f"UPDATE users SET language = 'Английский' WHERE user_id = {call.message.chat.id}")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=choose_country_text, parse_mode='Markdown', reply_markup=choose_country)

        if call.data == 'change_language':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=change_lanuage_text,
                                  parse_mode='Markdown', reply_markup=change_language)
        if call.data == 'russian_language_change':
            db_set(f"UPDATE users SET language = 'Русский' WHERE user_id = {call.message.chat.id}")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text="✅Язык успешно изменён!", parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'kazakh_language_change':
            db_set(f"UPDATE users SET language = 'Казахский' WHERE user_id = {call.message.chat.id}")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text="✅Тіл сәтті өзгертілді!", parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'ukrain_language_change':
            db_set(f"UPDATE users SET language = 'Украинский' WHERE user_id = {call.message.chat.id}")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text="✅Мова успішно змінена!", parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'english_language_change':
            db_set(f"UPDATE users SET language = 'Английский' WHERE user_id = {call.message.chat.id}")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text="✅Language successfully changed!", parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'user_back'))

        if call.data == 'russian_country':
            db_set(f"UPDATE users SET country = 'Россия' WHERE user_id = {call.message.chat.id}")
            add_trial_bonus(call.message.chat.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'subscribe_invite'), parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'subscribe_menu'))
        if call.data == 'kazakh_country':
            db_set(f"UPDATE users SET country = 'Казахстан' WHERE user_id = {call.message.chat.id}")
            add_trial_bonus(call.message.chat.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'subscribe_invite'), parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'subscribe_menu'))
        if call.data == 'ukrain_country':
            db_set(f"UPDATE users SET country = 'Украина' WHERE user_id = {call.message.chat.id}")
            add_trial_bonus(call.message.chat.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'subscribe_invite'), parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'subscribe_menu'))
        if call.data == 'other_country':
            db_set(f"UPDATE users SET country = 'Другое' WHERE user_id = {call.message.chat.id}")
            add_trial_bonus(call.message.chat.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'subscribe_invite'), parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'subscribe_menu'))

        if call.data == 'change_country':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=change_country_text,
                                  parse_mode='Markdown', reply_markup=change_country)
        if call.data == 'russian_country_change':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'update_text'))
            status = convert(call.message.chat.id, "Россия")
            if status:
                db_set(f"UPDATE users SET country = 'Россия' WHERE user_id = {call.message.chat.id}")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=get_interface(call.message.chat.id, 'success_changed_country'),
                                      parse_mode='Markdown',
                                      reply_markup=get_interface(call.message.chat.id, 'user_back'))
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=get_interface(call.message.chat.id, 'error_unknow2_text'),
                                      parse_mode='Markdown',
                                      reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'kazakh_country_change':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'update_text'))
            status = convert(call.message.chat.id, "Казахстан")
            if status:
                db_set(f"UPDATE users SET country = 'Казахстан' WHERE user_id = {call.message.chat.id}")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=get_interface(call.message.chat.id, 'success_changed_country'),
                                      parse_mode='Markdown',
                                      reply_markup=get_interface(call.message.chat.id, 'user_back'))
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=get_interface(call.message.chat.id, 'error_unknow2_text'),
                                      parse_mode='Markdown',
                                      reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'ukrain_country_change':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'update_text'))
            status = convert(call.message.chat.id, "Украина")
            if status:
                db_set(f"UPDATE users SET country = 'Украина' WHERE user_id = {call.message.chat.id}")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=get_interface(call.message.chat.id, 'success_changed_country'),
                                      parse_mode='Markdown',
                                      reply_markup=get_interface(call.message.chat.id, 'user_back'))
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=get_interface(call.message.chat.id, 'error_unknow2_text'),
                                      parse_mode='Markdown',
                                      reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'other_country_change':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'update_text'))
            status = convert(call.message.chat.id, "Другое")
            if status:
                db_set(f"UPDATE users SET country = 'Другое' WHERE user_id = {call.message.chat.id}")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=get_interface(call.message.chat.id, 'success_changed_country'),
                                      parse_mode='Markdown',
                                      reply_markup=get_interface(call.message.chat.id, 'user_back'))
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=get_interface(call.message.chat.id, 'error_unknow2_text'),
                                      parse_mode='Markdown',
                                      reply_markup=get_interface(call.message.chat.id, 'user_back'))

        if call.data == 'subscribed':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'update_text'))
            time.sleep(1)
            if is_user_in_channel(call.message.chat.id):
                country = db_get(f"SELECT country FROM users WHERE user_id = {call.message.chat.id}")
                if country == "Казахстан":
                    politika = ''
                    language = db_get(f"SELECT language FROM users WHERE user_id = {call.message.chat.id}")
                    if language == 'Русский':
                        politika = f"8. Вы соглашаетесь с условиями [Политики конфеденциальности и Договором публичной оферты на предоставление услуг]({politika_confedence})"
                    elif language == 'Казахский':
                        politika = f"8. Сіз [Құпиялық саясатының және қызметтерді көрсетуге арналған Қоғамдық ұсыныс келісімінің шарттарымен келісесіз]({politika_confedence})"
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                          text=f'{get_interface(call.message.chat.id, "terms_text")}\n{politika}',
                                          parse_mode='Markdown',
                                          reply_markup=get_interface(call.message.chat.id, 'terms_markup'))
                else:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                          text=get_interface(call.message.chat.id, 'terms_text'),
                                          parse_mode='Markdown',
                                          reply_markup=get_interface(call.message.chat.id, 'terms_markup'))
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=get_interface(call.message.chat.id, 'subscribe_invite'),
                                      parse_mode='Markdown',
                                      reply_markup=get_interface(call.message.chat.id, 'subscribe_menu'))

        if call.data == 'yes_terms':
            db_set(f"UPDATE users SET terms_of_use = {True} WHERE user_id = {call.message.chat.id}")
            if db_get(f'SELECT reffer FROM users WHERE user_id = {call.message.chat.id}') != 0:
                date_reg = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                add_bonus("referal", call.message.chat.id, date_reg, call.message.chat.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'welcome_text'), parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'welcome'))
        if call.data == 'menu_button':
            info = create_info_menu(call.message)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=info,
                                  parse_mode='Markdown'
                                  , reply_markup=get_interface(call.message.chat.id, 'user_menu'))
        if call.data == 'start_chat':
            if db_get(f"SELECT status FROM settings"):
                if db_get(f"SELECT status_chat FROM users WHERE user_id = {call.message.chat.id}"):
                    bot.send_message(call.message.chat.id, get_interface(call.message.chat.id, 'error_create_chat'),
                                     reply_markup=get_interface(call.message.chat.id, 'chat_settings'))
                else:
                    hi = get_interface(call.message.chat.id, 'welcome_chat_text')
                    db_set(f"UPDATE users SET status_chat = {True} WHERE user_id = {call.message.chat.id}")
                    msg = bot.send_message(call.message.chat.id, hi,
                                           reply_markup=get_interface(call.message.chat.id, 'chat_settings'))
                    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    db_insert_aaq(call.message.chat.id, '!', hi, f'{msg.message_id}-{call.message.id}', time_now,
                                  info_spending='-', model='gpt-4', free_api=False)
            else:
                bot.send_message(call.message.chat.id, get_interface(call.message.chat.id, "bot_out"))
        if call.data == 'end_chat':
            clear_messages(call.message.chat.id)
            cursor.execute(f"SELECT MAX(id_chat) FROM history_question_answer WHERE user_id = {call.message.chat.id};")
            id_chat = cursor.fetchone()[0]
            cursor.execute(
                f"SELECT message_id FROM history_question_answer WHERE user_id = {call.message.chat.id} AND status_chat = {False} AND id_chat = {id_chat}")
            messages = cursor.fetchall()
            for message in messages:
                msg = message[0].split('-')
                try:
                    bot.delete_message(call.message.chat.id, int(msg[0]))
                except:
                    pass
                try:
                    bot.delete_message(call.message.chat.id, int(msg[1]))
                except:
                    pass
                try:
                    bot.delete_message(call.message.chat.id, int(msg[2]))
                except:
                    pass
            db_set(f"UPDATE users SET status_chat = {False} WHERE user_id = {call.message.chat.id}")
            db_set(f"UPDATE history_question_answer SET status_chat = {True} WHERE user_id = {call.message.chat.id}")
            file = get_chat(call.message.chat.id)
            total_price_chat = get_chat_price(id_chat, call.message.chat.id)
            if total_price_chat > 0:
                country = db_get(f"SELECT country FROM users WHERE user_id = {call.message.chat.id}")
                if country == "Россия":
                    currency = "RUB"
                elif country == "Казахстан":
                    currency = "KZT"
                elif country == "Украина":
                    currency = "UAH"
                else:
                    currency = "USD"
                time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                db_insert_transactions(call.message.chat.id, 6, None, total_price_chat, currency, True, time_now, None,
                                       None, id_chat)
            bot.send_document(call.message.chat.id, document=open(file, 'rb'),
                              caption=get_interface(call.message.chat.id, "your_chat_text"),
                              reply_markup=get_interface(call.message.chat.id, "close_msg"))
            bot.send_message(call.message.chat.id, text=get_interface(call.message.chat.id, "end_chat_text"),
                             reply_markup=get_interface(call.message.chat.id, 'welcome'))
        if call.data == 'voice_off':
            msg3 = 1
            db_set(f"UPDATE users SET voice = false WHERE user_id = {call.message.chat.id}")
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.id)
            except:
                pass
            cursor.execute(f"SELECT MAX(id_chat) FROM history_question_answer WHERE user_id = {call.message.chat.id};")
            id_chat = cursor.fetchone()[0]
            res = db_all_get(
                f"SELECT answer, message_id, spending FROM history_question_answer WHERE user_id = {call.message.chat.id} AND id_chat = {id_chat} ORDER BY date_time DESC LIMIT 1;")
            info_db_spending = res[2].split('~')
            if len(info_db_spending) < 2:
                price_voice1 = 0
                total_tokens = 0
                total_price = 0
                total_price2 = 0
                balance = 0
                price_voice2 = 0
            else:
                price_voice1 = info_db_spending[0]
                total_tokens = info_db_spending[1]
                total_price = info_db_spending[2]
                total_price2 = info_db_spending[3]
                balance = info_db_spending[4]
                price_voice2 = info_db_spending[6]
            info = get_interface(call.message.chat.id, "rashod").replace("0", "{}").format(price_voice1,
                                                                                           price_voice2,
                                                                                           total_tokens,
                                                                                           total_price,
                                                                                           total_price2,
                                                                                           balance)
            msg = bot.send_message(call.message.chat.id, text=res[0] + info, parse_mode='Markdown',
                                   reply_markup=get_interface(call.message.chat.id, 'chat_settings'))
            msg_id = res[1].split('-')
            try:
                msg3 = int(msg_id[2])
            except:
                pass
            new_msg_id = f"{msg.id}-{int(msg_id[1])}-{msg3}"
            db_set(
                f"UPDATE history_question_answer SET message_id = '{new_msg_id}' WHERE message_id = '{res[1]}' AND user_id ={call.message.chat.id};")
        if call.data == 'voice_on':
            msg3 = 1
            db_set(f"UPDATE users SET voice = true WHERE user_id = {call.message.chat.id}")
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.id)
            except:
                pass
            cursor.execute(f"SELECT MAX(id_chat) FROM history_question_answer WHERE user_id = {call.message.chat.id};")
            id_chat = cursor.fetchone()[0]
            res = db_all_get(
                f"SELECT answer, message_id, spending FROM history_question_answer WHERE user_id = {call.message.chat.id} AND id_chat = {id_chat} ORDER BY date_time DESC LIMIT 1;")
            info_db_spending = res[2].split('~')
            if len(info_db_spending) < 2:
                price_voice1 = 0
                total_tokens = 0
                total_price = 0
                total_price2 = 0
                balance = 0
                price_voice2 = 0
            else:
                price_voice1 = info_db_spending[0]
                total_tokens = info_db_spending[1]
                total_price = info_db_spending[2]
                total_price2 = info_db_spending[3]
                balance = info_db_spending[4]
                price_voice2 = info_db_spending[6]
            info = get_interface(call.message.chat.id, "rashod").replace("0", "{}").format(price_voice1,
                                                                                           price_voice2,
                                                                                           total_tokens,
                                                                                           total_price,
                                                                                           total_price2,
                                                                                           balance)
            msg = bot.send_message(call.message.chat.id, text=res[0] + info, parse_mode='Markdown',
                                   reply_markup=get_interface(call.message.chat.id, 'chat_settings'))
            msg_id = res[1].split('-')
            try:
                msg3 = int(msg_id[2])
            except:
                pass
            new_msg_id = f"{msg.id}-{int(msg_id[1])}-{msg3}"
            db_set(
                f"UPDATE history_question_answer SET message_id = '{new_msg_id}' WHERE message_id = '{res[1]}' AND user_id ={call.message.chat.id};")
        if call.data == 'image_generation':
            db_result = db_all_get(f"SELECT * FROM users WHERE user_id = {call.message.chat.id}")
            country = db_result[11]
            balance = db_result[9]
            price_img = float(db_get('SELECT dalle FROM settings;'))
            cours_currency = db_get(f"SELECT cours_currency FROM settings").split('-')
            if country == "Россия":
                cours = cours_currency[0]
            elif country == "Казахстан":
                cours = cours_currency[1]
            elif country == "Украина":
                cours = cours_currency[2]
            else:
                cours = cours_currency[3]
            if price_img > float(balance) / float(cours):
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=get_interface(call.message.chat.id, "insufficient_funds"),
                                      parse_mode='Markdown',
                                      reply_markup=get_interface(call.message.chat.id, 'user_back'))
                return
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text=get_interface(call.message.chat.id, 'image_generation_start'),
                                        parse_mode='Markdown',
                                        reply_markup=get_interface(call.message.chat.id, 'user_back'))
            bot.register_next_step_handler(msg, generate_image, call.message)

        if call.data == 'update_user':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'update_text'))
            time.sleep(1)
            info = create_info_menu(call.message)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=info,
                                  parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'user_menu'))
        if call.data == 'buy_balance':
            pay_buttons = get_pay_button(call.message.chat.id)
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text=get_interface(call.message.chat.id, 'pay_balance_text'),
                                        parse_mode='Markdown',
                                        reply_markup=pay_buttons)
            bot.register_next_step_handler(msg, create_payment, call.message)
        if call.data == 'pay1_button':
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            create_payment2(call.message, "pay1")
        if call.data == 'pay2_button':
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            create_payment2(call.message, "pay2")
        if call.data == 'pay3_button':
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            create_payment2(call.message, "pay3")
        if call.data == 'pay4_button':
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            create_payment2(call.message, "pay4")
        if call.data == 'change_ai_model':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'change_ai_model_text'),
                                  parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'change_ai_model_markup'))
        if call.data == 'change_gpt4':
            db_set(f"UPDATE users SET ai_model = 'gpt-4-vision-preview' WHERE user_id = {call.message.chat.id}")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'update_text'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'success_changed_ai_model'),
                                  parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'change_gpt3':
            db_set(f"UPDATE users SET ai_model = 'gpt-3.5-turbo' WHERE user_id = {call.message.chat.id}")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'update_text'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'success_changed_ai_model'),
                                  parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'change_ai_voice':
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.id)
            except:
                pass
            language = db_get(f"SELECT language FROM users WHERE user_id = {call.message.chat.id}")
            if language == "Русский":
                media_group = [types.InputMediaAudio(open(audio_path, 'rb')) for audio_path in voice_ai_ru]
                bot.send_media_group(call.message.chat.id, media_group)
                bot.send_message(call.message.chat.id, text=voice_select_menu_ru,
                                 reply_markup=get_interface(call.message.chat.id, 'change_voice_model_menu_ru'))
            elif language == "Казахский":
                media_group = [types.InputMediaAudio(open(audio_path, 'rb')) for audio_path in voice_ai_kz]
                bot.send_media_group(call.message.chat.id, media_group)
                bot.send_message(call.message.chat.id, text=voice_select_menu_kz,
                                 reply_markup=get_interface(call.message.chat.id, 'change_voice_model_menu_kz'))
            elif language == "Украинский":
                media_group = [types.InputMediaAudio(open(audio_path, 'rb')) for audio_path in voice_ai_ua]
                bot.send_media_group(call.message.chat.id, media_group)
                bot.send_message(call.message.chat.id, text=voice_select_menu_ua,
                                 reply_markup=get_interface(call.message.chat.id, 'change_voice_model_menu_ua'))
            else:
                media_group = [types.InputMediaAudio(open(audio_path, 'rb')) for audio_path in voice_ai_en]
                bot.send_media_group(call.message.chat.id, media_group)
                bot.send_message(call.message.chat.id, text=voice_select_menu_en,
                                 reply_markup=get_interface(call.message.chat.id, 'change_voice_model_menu_en'))
        if call.data == 'voice1':
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 1)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 2)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 3)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 4)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 5)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 6)
            except:
                pass
            db_set(f"UPDATE users SET ai_voice = 'alloy' WHERE user_id = {call.message.chat.id}")
            bot.send_message(call.message.chat.id, text=get_interface(call.message.chat.id, 'success_ai_voice_changed'),
                             reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'voice2':
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 1)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 2)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 3)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 4)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 5)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 6)
            except:
                pass
            db_set(f"UPDATE users SET ai_voice = 'echo' WHERE user_id = {call.message.chat.id}")
            bot.send_message(call.message.chat.id, text=get_interface(call.message.chat.id, 'success_ai_voice_changed'),
                             reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'voice3':
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 1)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 2)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 3)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 4)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 5)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 6)
            except:
                pass
            db_set(f"UPDATE users SET ai_voice = 'fable' WHERE user_id = {call.message.chat.id}")
            bot.send_message(call.message.chat.id, text=get_interface(call.message.chat.id, 'success_ai_voice_changed'),
                             reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'voice4':
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 1)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 2)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 3)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 4)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 5)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 6)
            except:
                pass
            db_set(f"UPDATE users SET ai_voice = 'onyx' WHERE user_id = {call.message.chat.id}")
            bot.send_message(call.message.chat.id, text=get_interface(call.message.chat.id, 'success_ai_voice_changed'),
                             reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'voice5':
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 1)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 2)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 3)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 4)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 5)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 6)
            except:
                pass
            db_set(f"UPDATE users SET ai_voice = 'nova' WHERE user_id = {call.message.chat.id}")
            bot.send_message(call.message.chat.id, text=get_interface(call.message.chat.id, 'success_ai_voice_changed'),
                             reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'voice6':
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 1)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 2)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 3)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 4)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 5)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 6)
            except:
                pass
            db_set(f"UPDATE users SET ai_voice = 'shimmer' WHERE user_id = {call.message.chat.id}")
            bot.send_message(call.message.chat.id, text=get_interface(call.message.chat.id, 'success_ai_voice_changed'),
                             reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'my_transactions':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'process_transactions'))
            file = get_all_transactions(call.message.chat.id)
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.id)
            except:
                pass
            bot.send_document(call.message.chat.id, document=open(file, 'rb'),
                              caption=get_interface(call.message.chat.id, "your_transactions_text"),
                              reply_markup=get_interface(call.message.chat.id, "close_msg"))
            info = create_info_menu(call.message)
            bot.send_message(chat_id=call.message.chat.id, text=info,
                             parse_mode='Markdown',
                             reply_markup=get_interface(call.message.chat.id, 'user_menu'))
        if call.data == 'chats_menu':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'chats_menu_text'),
                                  reply_markup=get_interface(call.message.chat.id, 'chats_menu'))
        if call.data == 'get_all_chats':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'process_chats'))
            file = get_all_chats(call.message.chat.id)
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.id)
            except:
                pass
            bot.send_document(call.message.chat.id, document=open(file, 'rb'),
                              caption=get_interface(call.message.chat.id, "your_chats_text"),
                              reply_markup=get_interface(call.message.chat.id, "close_msg"))
            info = create_info_menu(call.message)
            bot.send_message(chat_id=call.message.chat.id, text=info,
                             parse_mode='Markdown',
                             reply_markup=get_interface(call.message.chat.id, 'user_menu'))
        if call.data == 'get_one_chat':
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text=get_interface(call.message.chat.id, 'input_chat_number'),
                                        reply_markup=get_interface(call.message.chat.id, 'user_back'))
            bot.register_next_step_handler(msg, get_chat_settings, call.message)
        if call.data == 'delete_history':
            db_set(f'DELETE FROM history_question_answer WHERE user_id = {call.message.chat.id};')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'delete_history_complete'),
                                  parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'price_info':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'price_info'), parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'user_back'))
        if call.data == 'welcome_menu':
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=get_interface(call.message.chat.id, 'welcome_text'), parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'welcome'))
        if call.data == 'back_user':
            info = create_info_menu(call.message)
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=info,
                                  parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'user_menu'))
        if call.data == 'back_user_from_voice':
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 1)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 2)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 3)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 4)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 5)
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id - 6)
            except:
                pass
            info = create_info_menu(call.message)
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=info,
                                  parse_mode='Markdown',
                                  reply_markup=get_interface(call.message.chat.id, 'user_menu'))
        if call.data == 'close_msg':
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.id)
            except:
                bot.answer_callback_query(callback_query_id=call.id, text=get_interface(call.message.chat.id, 'error_delete_msg'))

        if call.data == "update_admin":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text="Обновляю")
            time.sleep(1)
            info = create_info_adminmenu()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=info,
                                  reply_markup=admin_menu)
        if call.data == "add_balance":
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text="Введите ID пользователя и значение пополняемого счета\nПример: 123456789-50\nВ данном примере 123456789 это ID пользователя, а 50 это количество бонусов, которые ему будут добавлены.",
                                        reply_markup=admin_back)
            bot.register_next_step_handler(msg, add_balance_user, call.message)
        if call.data == 'status_bot':
            if db_get(f"SELECT status FROM settings"):
                status = "работает"
            else:
                status = "отключен"

            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text='Текущее состояние бота {}\nВведите "1" или "0", если хотите включить или отключить бота.'.format(
                                            status),
                                        reply_markup=admin_back)
            bot.register_next_step_handler(msg, set_new_status, call.message)
        if call.data == 'token_message':
            tokens = db_get(f"SELECT tokens FROM settings")
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text="Текущее количество токенов на одно сообщение: {}\nВведите новое значение токенов за одно сообщение от 1 до 4000".format(
                                            tokens),
                                        reply_markup=admin_back)
            bot.register_next_step_handler(msg, set_new_tokens, call.message)
        if call.data == 'temperature_message':
            temp = db_get(f"SELECT temperature FROM settings")
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text="Текущее температура модели: {}\nВведите новое значение от 0.00 до 1.00".format(
                                            temp),
                                        reply_markup=admin_back)
            bot.register_next_step_handler(msg, set_new_temp, call.message)
        if call.data == 'bonus_referal':
            referal_b = db_get(f"SELECT referal_bonus FROM settings")
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text="Текущий бонус для рефералов: {}\nВведите новое значение".format(
                                            referal_b),
                                        reply_markup=admin_back)
            bot.register_next_step_handler(msg, set_new_referal_bonus, call.message)
        if call.data == 'bonus_reffer':
            reffer_b = db_get(f"SELECT reffer_bonus FROM settings")
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text="Текущий бонус для реферов: {}\nВведите новое значение".format(
                                            reffer_b),
                                        reply_markup=admin_back)
            bot.register_next_step_handler(msg, set_new_reffer_bonus, call.message)
        if call.data == 'trial_bonus':
            trial_b = db_get(f"SELECT trial_bonus FROM settings")
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text=f"Текущий триал бонус: {trial_b}\nВведите новое значение",
                                        reply_markup=admin_back)
            bot.register_next_step_handler(msg, set_new_trial_bonus, call.message)
        if call.data == 'gpt-4_price':
            gpt4 = db_get(f"SELECT gpt4 FROM settings")
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text=f"Текущий прайс GPT-4: {gpt4}\nВведите новое значение",
                                        reply_markup=admin_back)
            bot.register_next_step_handler(msg, set_new_gpt4_price, call.message)
        if call.data == 'gpt-3_price':
            gpt3 = db_get(f"SELECT gpt3 FROM settings")
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text=f"Текущий прайс GPT-3.5-turbo: {gpt3}\nВведите новое значение",
                                        reply_markup=admin_back)
            bot.register_next_step_handler(msg, set_new_gpt3_price, call.message)
        if call.data == 'whisper_price':
            whisper = db_get(f"SELECT whisper FROM settings")
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text=f"Текущий прайс Whisper: {whisper}\nВведите новое значение",
                                        reply_markup=admin_back)
            bot.register_next_step_handler(msg, set_new_whisper_price, call.message)
        if call.data == 'cashback_button':
            cashback = db_get(f"SELECT cashback FROM settings")
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text="Текущий кешбек с каждой покупки: {} %\nВведите новое значение".format(
                                            cashback),
                                        reply_markup=admin_back)
            bot.register_next_step_handler(msg, set_new_cashback, call.message)
        if call.data == 'free_api_button':
            status = db_get(f"SELECT free_api FROM settings")
            if status:
                info = 'подключен'
            else:
                info = 'отключен'
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text="Статус бесплатного API: {}\nВведите: \n1 - чтобы включить\n0- чтобы выключить".format(
                                            info),
                                        reply_markup=admin_back)
            bot.register_next_step_handler(msg, set_on_off_free_api, call.message)
        if call.data == 'all_message':
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                        text="Введите сообщение, которое будет отправлено для всех незаблокированных пользователей.",
                                        reply_markup=admin_back)
            bot.register_next_step_handler(msg, all_message, call.message)
        if call.data == 'back_admin':
            info = create_info_adminmenu()
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=info,
                                  reply_markup=admin_menu)


def check_if_successful_payment(request):
    try:
        if request.json["event"] == "payment.succeeded":
            return True
    except KeyError:
        return False

    return False

@app.route('/notify', methods=['POST'])
def process_request():
    order_id = request.json["object"]["metadata"]["order_id"]
    user_id = request.json["object"]["metadata"]["user_id"]
    order_id = f"{user_id}-{order_id}"
    print(order_id)
    if check_if_successful_payment(request):
        if (db_get(f"SELECT status FROM transactions_history WHERE merchant_order_id = '{order_id}'") == False):
            payment_approved(order_id)
            return "YES", 200
    else:
        return "NO", 403

@app.route('/notify_robokassa', methods=['GET'])
def result_payment():
    if request.access_route[0] not in ips:
        abort(403)
    param_request = parse_response(str(request))
    cost = decimal.Decimal(param_request['OutSum'])
    number = int(param_request['InvId'])
    signature = param_request['SignatureValue']
    Shp_id = request.values['Shp_id']
    order_id = f"{Shp_id}-{number}"
    if check_signature_result(number, cost, signature, pass_test2, 'Shp_id=' + Shp_id):
        if (db_get(f"SELECT status FROM transactions_history WHERE merchant_order_id = '{order_id}'") == False):
            payment_approved(order_id)
        return f'OK{param_request["InvId"]}'
    return "bad sign"

def delete_null_chats():
    try:
        db_set(
            f"DELETE FROM history_question_answer WHERE question = 'ERROR' AND answer = 'ERROR' AND status_chat = True")
        db_set("""DELETE FROM history_question_answer AS hqa
                WHERE status_chat = True
                  AND NOT EXISTS (
                    SELECT 1
                    FROM history_question_answer AS sub_hqa
                    WHERE sub_hqa.user_id = hqa.user_id
                      AND sub_hqa.id_chat = hqa.id_chat
                      AND sub_hqa.message_id != hqa.message_id
                  )""")
    except:
        pass

def update_cours():
    try:
        cours_RUB = round(float(get_exchange_rate("USD", "RUB")) * 1.06, 2)
        cours_KZT = round(float(get_exchange_rate("USD", "KZT")) * 1.06, 2)
        cours_UAH = round(float(get_exchange_rate("USD", "UAH")) * 1.06, 2)
        cours_currency = f"{cours_RUB}-{cours_KZT}-{cours_UAH}-1"
        db_set(f"UPDATE settings SET cours_currency = '{cours_currency}'")
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Обновлены курсы валют! {cours_currency}")
    except:
        pass

def clear_tg_messages():
    cursor.execute(f"""
                    SELECT message_id, user_id
                    FROM history_question_answer
                    WHERE date_time > NOW() - INTERVAL '48 hours'
                      AND date_time <= NOW() - INTERVAL '24 hours'
                      AND status_chat = {False};
                """)
    list_messages = cursor.fetchall()
    user_ids = list(set(messages[1] for messages in list_messages))
    # Удаление сообщений через Telegram Bot API
    for message in list_messages:
        chat_id = message[1]
        try:
            msg = message[0].split('-')
        except:
            msg = [1, 2, 3]
        try:
            bot.delete_message(chat_id, int(msg[0]))
        except:
            pass
        try:
            bot.delete_message(chat_id, int(msg[1]))
        except:
            pass
        try:
            bot.delete_message(chat_id, int(msg[2]))
        except:
            pass
    for user_id in user_ids:
        file = get_chat(user_id)
        cursor.execute(f"SELECT MAX(id_chat) FROM history_question_answer WHERE user_id = {user_id};")
        id_chat = cursor.fetchone()[0]
        total_price_chat = get_chat_price(id_chat, user_id)
        if total_price_chat > 0:
            country = db_get(f"SELECT country FROM users WHERE user_id = {user_id}")
            if country == "Россия":
                currency = "RUB"
            elif country == "Казахстан":
                currency = "KZT"
            elif country == "Украина":
                currency = "UAH"
            else:
                currency = "USD"
            time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db_insert_transactions(user_id, 6, None, total_price_chat, currency, True, time_now, None, None,
                                   id_chat)
        try:
            bot.send_document(user_id, document=open(file, 'rb'),
                              caption=get_interface(user_id, "your_chat_text"),
                              reply_markup=get_interface(user_id, "close_msg"))
            bot.send_message(user_id, text=get_interface(user_id, "end_chat_text"),
                             reply_markup=get_interface(user_id, 'welcome'))
        except:
            pass
    if user_ids:
        update_query2 = """
                    UPDATE users
                    SET status_chat = False
                    WHERE user_id IN %s;
                    """
        cursor.execute(update_query2, (tuple(user_ids),))
        update_query = """
            UPDATE history_question_answer
            SET status_chat = True
            WHERE user_id IN %s;
            """
        cursor.execute(update_query, (tuple(user_ids),))
    print(f"Чистка не завершенных диалогов прошла успешно! Обработано пользователей: {len(user_ids)}")
    return

def mainloop():
    while True:
        try:
            bot.infinity_polling()
        except:
            time.sleep(5)

def kassa():
    try:
        app.run(host=ip_server, port=443, ssl_context=('server.crt', 'server.key'))
    except:
        time.sleep(5)
        app.run(host=ip_server, port=443, ssl_context=('server.crt', 'server.key'))

def cours_check():
    schedule.every(3).hours.do(update_cours)
    schedule.every(15).seconds.do(delete_null_chats)
    schedule.every(10).minutes.do(clear_tg_messages)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    thread1 = threading.Thread(target=mainloop)
    thread1.start()
    thread2 = threading.Thread(target=kassa)
    thread2.start()
    thread3 = threading.Thread(target=cours_check)
    thread3.start()

