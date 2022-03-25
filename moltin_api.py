import requests


def get_access_token(client_id, client_secret):
    url = 'https://api.moltin.com/oauth/access_token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()


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


def get_or_create_cart(access_token, cart_id, currency='USD'):
    url = f'https://api.moltin.com/v2/carts/{cart_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-MOLTIN-CURRENCY': currency
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


def add_cart_item(access_token, cart_id, item_id,
                  item_quantity, currency='USD'):
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-MOLTIN-CURRENCY': currency
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


def remove_cart_item(access_token, cart_id, item_id):
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items/{item_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.delete(url, headers=headers)
    return response.ok


def create_customer(access_token, email, name=None):
    url = 'https://api.moltin.com/v2/customers'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    customer = {
        'data': {
            'type': 'customer',
            'name': name if name else email.split('@')[0],
            'email': email,
        },
    }

    response = requests.post(url, headers=headers, json=customer)
    response.raise_for_status()
    return response.json()


def get_customer(access_token, customer_id):
    url = f'https://api.moltin.com/v2/customers/{customer_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
