"""
Работает с этими модулями:
python-telegram-bot==11.1.0
redis==3.2.1
"""
from environs import Env
import logging
import redis
import shop_api

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

_database = None
_shop_token = ''


def start(bot, update):
    """
    Хэндлер для состояния START.

    Бот отвечает пользователю фразой "Привет!" и переводит его в состояние ECHO.
    Теперь в ответ на его команды будет запускаеться хэндлер echo.
    """
    products = shop_api.get_products(_shop_token)
    keyboard = [
        [
            InlineKeyboardButton(
                product['attributes']['name'], callback_data=product["id"]),
        ] for product in products
    ]
    markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(text='Привет! Выбери', reply_markup=markup)

    return 'HANDLE_MENU'

def handle_menu(bot,update):
    query = update.callback_query
    query.answer()
    product_id = query.data
    product = shop_api.get_product(_shop_token, product_id)
    description = "\n".join(
        [
            product['name'],
            "\n",
            product["description"],
        ]
    )
    query.edit_message_text(text=description)
    return 'START'


def handle_users_reply(bot, update):
    """
    Функция, которая запускается при любом сообщении от пользователя и решает как его обработать.
    Эта функция запускается в ответ на эти действия пользователя:
        * Нажатие на inline-кнопку в боте
        * Отправка сообщения боту
        * Отправка команды боту
    Она получает стейт пользователя из базы данных и запускает соответствующую функцию-обработчик (хэндлер).
    Функция-обработчик возвращает следующее состояние, которое записывается в базу данных.
    Если пользователь только начал пользоваться ботом, Telegram форсит его написать "/start",
    поэтому по этой фразе выставляется стартовое состояние.
    Если пользователь захочет начать общение с ботом заново, он также может воспользоваться этой командой.
    """
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu
    }
    state_handler = states_functions[user_state]
    # Если вы вдруг не заметите, что python-telegram-bot перехватывает ошибки.
    # Оставляю этот try...except, чтобы код не падал молча.
    # Этот фрагмент можно переписать.
    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
    env = Env()
    env.read_env()
    global _database
    if _database is None:
        database_password = env("REDIS_DB_PASSWORD")
        database_host = env("REDIS_DB_HOST")
        database_port = env("REDIS_DB_PORT")
        _database = redis.Redis(
            host=database_host, port=database_port, password=database_password)
    return _database


if __name__ == '__main__':
    env = Env()
    env.read_env()
    client_id = env("ELASTICPATH_CLIENT_ID")
    _shop_token = shop_api.get_access_token(client_id)
    telegram_api_key = env("TELEGRAM_API_KEY")
    updater = Updater(telegram_api_key)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()