from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from moltin_api import get_products


def get_products_menu(moltin_token):
    products = get_products(moltin_token)
    parsed_products = parse_products(products)
    extra_buttons = {
        'Корзина': 'cart',
    }
    current_buttons = {**parsed_products, **extra_buttons}
    keyboard = []
    for button_name, button_id in current_buttons.items():
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
    stock = product['meta']['stock']['level']
    main_image = product['relationships'].get('main_image')

    product_description = {
        'name': name,
        'description': description,
        'price': price,
        'stock': stock,
        'image_id': main_image['data']['id'] if main_image else ''
    }
    return product_description


def parse_cart(cart):
    total_price = cart['meta']['display_price']['with_tax']['formatted']
    cart_description = []

    for cart_item in cart['data']:
        item_name = cart_item['name']
        item_description = cart_item['description']
        item_quantity = cart_item['quantity']
        item_price = cart_item['meta']['display_price']['with_tax']
        item_unit_price = item_price['unit']['formatted']
        item_value_price = item_price['value']['formatted']

        cart_item_description = {
            'name': item_name,
            'description': item_description,
            'quantity': item_quantity,
            'unit_price': item_unit_price,
            'value_price': item_value_price
        }
        cart_description.append(cart_item_description)
    return {
        'total_price': total_price,
        'cart_description': cart_description
    }
