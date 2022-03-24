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
            [InlineKeyboardButton(text=button_name, callback_data=button_id)]
        )

    return InlineKeyboardMarkup(keyboard)


def parse_products(products):
    products_names_with_ids = {}
    for product in products['data']:
        product_name = product['name']
        product_id = product['id']
        products_names_with_ids[product_name] = product_id
    return products_names_with_ids


def parse_product(product):
    product = product['data']
    name = product['name']
    description = product['description']
    price = product['meta']['display_price']['with_tax']['formatted']
    weight = product['weight']['kg']
    stock = product['meta']['stock']['level']
    main_image = product['relationships'].get('main_image')

    product_description = {
        'name': name,
        'description': description,
        'price': price,
        'weight': weight,
        'stock': stock,
        'image_id': main_image['data']['id'] if main_image else ''
    }
    return product_description
