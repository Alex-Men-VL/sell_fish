import pprint

import requests
from environs import Env


def get_access_token(client_id, client_secret):
    url = 'https://api.moltin.com/oauth/access_token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=payload)
    token_description = response.json()
    return {'token': token_description['access_token'],
            'expires': token_description['expires']}


def get_products(access_token):
    url = 'https://api.moltin.com/v2/products'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_product(access_token, product_id):
    url = f'https://api.moltin.com/v2/products/{product_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_product_main_image_url(access_token, image_id):
    url = f'https://api.moltin.com/v2/files/{image_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['link']['href']


def get_or_create_cart(access_token, cart_id):
    url = f'https://api.moltin.com/v2/carts/{cart_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-MOLTIN-CURRENCY': 'USD'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_cart_items(access_token, cart_id):
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def add_cart_item(access_token, cart_id, item_id, item_quantity):
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-MOLTIN-CURRENCY': 'USD'
    }

    cart_item = {
        'data': {
            'id': item_id,
            'type': 'cart_item',
            'quantity': item_quantity,
        },
    }
    response = requests.post(url, headers=headers, json=cart_item)
    response.raise_for_status()
    return response.json()


def main():
    env = Env()
    env.read_env()

    client_id = env.str('CLIENT_ID')
    client_secret = env.str('CLIENT_SECRET')
    access_token = get_access_token(client_id, client_secret)
    # print(access_token['token'])
    products = get_products(access_token['token'])
    # pprint.pprint(get_product(access_token['token'], products['data'][0]['id']))

    cart = get_or_create_cart(access_token['token'], '154383987')
    pprint.pprint(cart)
    pprint.pprint(get_cart_items(access_token['token'], '154383987'))
    # add_cart_item(access_token, cart['data']['id'],
    #               products['data'][0]['id'], 1)


if __name__ == '__main__':
    main()
