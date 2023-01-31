from environs import Env
import redis
import elasticpath_shop_api
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Message
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)
import re

_database = None


def start(update: Update, context) -> str:
    elasticpath_shop_api.get_cart(shop_token, update.effective_user.id)
    menu(update.message)

    return 'HANDLE_MENU'


def menu(message: Message):
    products = elasticpath_shop_api.get_products(shop_token)

    keyboard = [
        [
            InlineKeyboardButton(
                product['attributes']['name'], callback_data=product["id"]),
        ] for product in products
    ]
    keyboard.append([InlineKeyboardButton("Корзина", callback_data="cart")])
    markup = InlineKeyboardMarkup(keyboard)

    message.reply_text(text='Выберите товар:', reply_markup=markup)


def show_products(message: Message, product_id: str):
    product = elasticpath_shop_api.get_product(shop_token, product_id)
    product_photo_url = elasticpath_shop_api.get_file_link(
        shop_token, product_id)
    keyboard = [
        [
            InlineKeyboardButton("1 кг", callback_data=f"{product_id},1"),
            InlineKeyboardButton("5 кг", callback_data=f"{product_id},5"),
            InlineKeyboardButton("10 кг", callback_data=f"{product_id},10"),
        ],
        [
            InlineKeyboardButton("Корзина", callback_data="cart")
        ],
        [
            InlineKeyboardButton("В меню", callback_data="back"),
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    description = "\n".join(
        [
            product['attributes']["name"],
            "\n",
            product['attributes']["description"],
        ]
    )
    message.reply_photo(
        product_photo_url, caption=description, reply_markup=markup)


def view_cart(message: Message, cart_reference: str):
    cart_description = elasticpath_shop_api.get_cart_items(
        shop_token, cart_reference)
    total = cart_description["meta"]["display_price"]["with_tax"]["formatted"]
    cart_items = []
    keyboard = [[InlineKeyboardButton("В меню", callback_data="back")],
                [InlineKeyboardButton("Оплатить", callback_data="payment")]]
    for item in cart_description["data"]:
        cost = item['meta']['display_price']['with_tax']
        item_description = [
            item['name'],
            f"{cost['unit']['formatted']} за кг",
            f"{item['quantity']} кг на сумму {cost['value']['formatted']}",
        ]
        keyboard.append([InlineKeyboardButton(
            f"Убрать {item['name']}", callback_data=item["id"])])
        cart_items.extend(item_description)
    cart_items.append(f"Итого: {total}")
    cart_text = "\n".join(cart_items)

    markup = InlineKeyboardMarkup(keyboard)

    message.reply_text(cart_text, reply_markup=markup)


def handle_description(update: Update, context) -> str:
    query = update.callback_query
    query.answer()
    if query.data == "back":
        query.delete_message()
        menu(query.message)

        return 'HANDLE_MENU'

    if query.data == "cart":
        query.delete_message()
        view_cart(query.message, update.effective_user.id)

        return 'HANDLE_CART'

    product_id, quantity = query.data.split(",")
    elasticpath_shop_api.add_product(
        token=shop_token,
        cart_reference=update.effective_user.id,
        product_id=product_id,
        quantity=int(quantity)
    )

    return 'HANDLE_DESCRIPTION'


def handle_cart(update: Update, context) -> str:
    query = update.callback_query
    query.answer()
    if query.data == "back":
        query.delete_message()
        menu(query.message)

        return 'HANDLE_MENU'

    if query.data == "payment":
        query.message.reply_text("Пожалуйста, укажите Ваш Email")

        return 'HANDLE_WAITING_EMAIL'

    elasticpath_shop_api.remove_cart_item(
        shop_token, update.effective_user.id, query.data,)
    query.delete_message()
    view_cart(query.message, cart_reference=update.effective_user.id)

    return 'HANDLE_CART'


def handle_input_email(update: Update, context) -> str:
    user_email = update.message.text
    if not re.match('[^@]+@[^@]+\.[^@]+', user_email):
        update.message.reply_text(
            "Ошибка, пожалуйста, укажите корректный адрес электронной почты")

        return 'HANDLE_WAITING_EMAIL'
    else:
        user_name = update.effective_user.full_name
        elasticpath_shop_api.create_customer(
            token=shop_token,
            name=user_name,
            email=user_email,
        )
        menu(update.message)

        return 'HANDLE_MENU'


def handle_menu(update: Update, context) -> str:
    query = update.callback_query
    query.answer()
    query.delete_message()
    if query.data == "cart":
        view_cart(query.message, update.effective_user.id)

        return 'HANDLE_CART'

    show_products(query.message, product_id=query.data)

    return 'HANDLE_DESCRIPTION'


def handle_users_reply(update: Update, context):
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
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'HANDLE_WAITING_EMAIL': handle_input_email
    }
    state_handler = states_functions[user_state]

    try:
        next_state = state_handler(update, context)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():

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
    telegram_api_key = env("TELEGRAM_API_KEY")
    shop_token = elasticpath_shop_api.get_access_token(client_id)
    updater = Updater(telegram_api_key)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
