import logging
from datetime import datetime

from environs import Env
from telegram import Bot
from telegram.ext import Updater, CallbackQueryHandler, MessageHandler, \
    CommandHandler, Filters, PicklePersistence

from logs_handler import TelegramLogsHandler
from moltin_api import get_access_token
from tg_lib import get_products_menu

logger = logging.getLogger(__file__)


def handle_start_message(update, context):
    reply_markup = get_products_menu(context.bot_data['moltin_token'])
    update.message.reply_text(text='Please choose:',
                              reply_markup=reply_markup)
    return 'ECHO'


def echo(update, context):
    query = update.callback_query
    context.bot.edit_message_text(query.data,
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id)
    return 'ECHO'


def handle_users_reply(update, context):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return

    moltin_token_expiration = context.bot_data['token_expiration']
    if moltin_token_expiration <= datetime.timestamp(datetime.now()):
        moltin_access_token = get_access_token(
            context.bot_data['client_id'],
            context.bot_data['client_secret']
        )
        context.bot_data.update(
            {
                'moltin_token': moltin_access_token['token'],
                'token_expiration': moltin_access_token['expires'],
            }
        )

    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = context.user_data['state']

    states_functions = {
        'START': handle_start_message,
        'ECHO': echo
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
    logger.info('Бот запущен')

    updater.dispatcher.add_handler(
        CallbackQueryHandler(handle_users_reply)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text, handle_users_reply)
    )
    updater.dispatcher.add_handler(
        CommandHandler('start', handle_users_reply)
    )

    moltin_access_token = get_access_token(client_id, client_secret)
    updater.dispatcher.bot_data.update(
        {
            'moltin_token': moltin_access_token['token'],
            'token_expiration': moltin_access_token['expires'],
            'client_id': client_id,
            'client_secret': client_secret
        }
    )
    print(updater.dispatcher.bot_data)

    try:
        updater.start_polling()
        updater.idle()
    except Exception as err:
        logger.error(err)


if __name__ == '__main__':
    main()
