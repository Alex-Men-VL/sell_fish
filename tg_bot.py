import logging
import re
from datetime import datetime

import requests
from environs import Env
from telegram import (
    Bot,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Updater,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    Filters,
    PicklePersistence
)

from logs_handler import TelegramLogsHandler
from moltin_api import (
    get_access_token,
    get_product,
    get_or_create_cart,
    add_cart_item,
    get_cart_items,
    remove_cart_item,
    create_customer
)
from tg_lib import (
    get_products_menu,
    parse_cart,
    send_cart_description,
    send_product_description,
    send_main_menu
)

logger = logging.getLogger(__file__)


def handle_start(update, context):
    reply_markup = get_products_menu(context.bot_data['moltin_token'])
    update.message.reply_text(text='Please choose:',
                              reply_markup=reply_markup)
    context.user_data['reply_markup'] = reply_markup
    return 'HANDLE_MENU'


def handle_menu(update, context):
    moltin_token = context.bot_data['moltin_token']
    chat_id = context.user_data['chat_id']
    user_reply = context.user_data['user_reply']

    if user_reply == 'cart':
        user_cart = get_cart_items(moltin_token, chat_id)
        cart_description = parse_cart(user_cart)
        send_cart_description(context, cart_description)
        return 'HANDLE_CART'

    context.user_data['product_id'] = user_reply

    product = get_product(moltin_token, user_reply)
    product_main_image = product['relationships'].get('main_image')

    product_description = {
        'name': product['data']['name'],
        'description': product['data']['description'],
        'price': product['data']['meta']['display_price']['with_tax'][
            'formatted'
        ],
        'stock': product['data']['meta']['stock']['level'],
        'image_id': product_main_image['data']['id'] if product_main_image
        else ''
    }

    send_product_description(context, product_description)
    return 'HANDLE_DESCRIPTION'


def handle_description(update, context):
    chat_id = context.user_data['chat_id']
    message_id = context.user_data['message_id']
    moltin_token = context.bot_data['moltin_token']
    product_id = context.user_data['product_id']
    user_reply = context.user_data['user_reply']

    if user_reply == 'menu':
        send_main_menu(context, chat_id, message_id)
        return 'HANDLE_MENU'
    elif user_reply.isdigit():
        user_cart = get_or_create_cart(moltin_token, chat_id)
        try:
            add_cart_item(moltin_token, user_cart['data']['id'],
                          product_id, item_quantity=int(user_reply))
        except requests.exceptions.HTTPError:
            context.bot.answer_callback_query(
                callback_query_id=update.callback_query.id,
                text='???? ?????????????? ???????????????? ?????????? ?? ??????????????'
            )
        else:
            context.bot.answer_callback_query(
                callback_query_id=update.callback_query.id,
                text='?????????? ???????????????? ?? ??????????????'
            )
    return 'HANDLE_DESCRIPTION'


def handle_cart(update, context):
    chat_id = context.user_data['chat_id']
    message_id = context.user_data['message_id']
    user_reply = context.user_data['user_reply']
    moltin_token = context.bot_data['moltin_token']

    if user_reply == 'menu':
        send_main_menu(context, chat_id, message_id)
        return 'HANDLE_MENU'
    elif user_reply == 'pay':
        message = '????????????????????, ???????????????? ???????? ?????????? ?????? ?????????? ?? ????????'
        context.bot.send_message(text=message,
                                 chat_id=chat_id)
        return 'WAITING_EMAIL'

    item_removed = remove_cart_item(moltin_token, chat_id, user_reply)
    if item_removed:
        context.bot.answer_callback_query(
            callback_query_id=update.callback_query.id,
            text='?????????? ???????????? ???? ??????????????'
        )
        user_cart = get_cart_items(moltin_token, chat_id)
        cart_description = parse_cart(user_cart)
        send_cart_description(context, cart_description)
    else:
        context.bot.answer_callback_query(
            callback_query_id=update.callback_query.id,
            text='?????????? ???? ?????????? ???????? ???????????? ???? ??????????????'
        )
    return 'HANDLE_CART'


def handle_email(update, context):
    chat_id = context.user_data['chat_id']
    user_email = context.user_data['user_reply']
    moltin_token = context.bot_data['moltin_token']

    email_pattern = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
    if not re.fullmatch(email_pattern, user_email):
        message = '?????????? ?????????????? ???? ??????????. ?????????????????? ?????????? ?????? ??????.'
        update.message.reply_text(text=message)
        return 'WAITING_EMAIL'

    if not context.bot_data.get('customers'):
        context.bot_data['customers'] = {}

    if not context.bot_data['customers'].get(chat_id):
        customer = create_customer(moltin_token, user_email)
        context.bot_data['customers'][chat_id] = customer['data']['id']
    message = f'???? ?????????? ?????? ??????????: {user_email}'
    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text='?? ????????', callback_data='menu')]
        ]
    )
    update.message.reply_text(text=message, reply_markup=reply_markup)
    return 'HANDLE_CART'


def handle_users_reply(update, context):
    if message := update.message:
        user_reply = message.text
        chat_id = message.chat_id
        message_id = message.message_id
    elif query := update.callback_query:
        user_reply = query.data
        chat_id = query.message.chat_id
        message_id = query.message.message_id
    else:
        return

    context.user_data.update(
        {
            'user_reply': user_reply,
            'chat_id': chat_id,
            'message_id': message_id
        }
    )

    if (not (token_expiration := context.bot_data.get('token_expiration')) or
            token_expiration <= datetime.timestamp(datetime.now())):
        moltin_access_token = get_access_token(
            context.bot_data['client_id'],
            context.bot_data['client_secret']
        )
        context.bot_data.update(
            {
                'moltin_token': moltin_access_token['access_token'],
                'token_expiration': moltin_access_token['expires'],
            }
        )

    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = context.user_data['state']

    states_functions = {
        'START': handle_start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': handle_email
    }
    state_handler = states_functions[user_state]

    try:
        next_state = state_handler(update, context)
        context.user_data['state'] = next_state
    except Exception as err:
        logger.error(err)


def main():
    env = Env()
    env.read_env()

    logging.basicConfig(level=logging.INFO)

    bot_token = env.str('TG_BOT_TOKEN')
    dev_bot_token = env.str('TG_DEV_BOT_TOKEN')
    tg_dev_chat_id = env.str('TG_DEV_CHAT_ID')
    client_id = env.str('CLIENT_ID')
    client_secret = env.str('CLIENT_SECRET')

    dev_bot = Bot(token=dev_bot_token)
    tg_logger = TelegramLogsHandler(dev_bot, tg_dev_chat_id)
    logger.addHandler(tg_logger)

    persistence = PicklePersistence(filename='tg_bot.pickle')

    updater = Updater(token=bot_token, persistence=persistence)
    logger.info('?????? ??????????????')

    updater.dispatcher.add_handler(
        CallbackQueryHandler(handle_users_reply)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text, handle_users_reply)
    )
    updater.dispatcher.add_handler(
        CommandHandler('start', handle_users_reply)
    )

    updater.dispatcher.bot_data.update(
        {
            'client_id': client_id,
            'client_secret': client_secret
        }
    )
    updater.dispatcher.bot.delete_my_commands()
    updater.dispatcher.bot.set_my_commands(
        language_code='ru',
        commands=[BotCommand('start', '?????????????? ?? ????????')]
    )

    try:
        updater.start_polling()
        updater.idle()
    except Exception as err:
        logger.error(err)


if __name__ == '__main__':
    main()
