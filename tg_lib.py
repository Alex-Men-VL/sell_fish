from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from moltin_api import get_products


def get_products_menu(moltin_token):
    products = get_products(moltin_token)
    parsed_products = parse_products(products)
    keyboard_markup = generate_keyboard_markup(parsed_products)
    return keyboard_markup


def generate_keyboard_markup(buttons: dict):
    keyboard = []
    for button_name, button_id in buttons.items():
        keyboard.append(
            [InlineKeyboardButton(button_name, callback_data=button_id)]
        )

    return InlineKeyboardMarkup(keyboard)


def parse_products(products):
    products_names_with_ids = {}
    for product in products['data']:
        product_name = product['name']
        product_id = product['id']
        products_names_with_ids[product_name] = product_id
    return products_names_with_ids
