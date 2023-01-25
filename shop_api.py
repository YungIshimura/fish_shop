import requests
from environs import Env
from pprint import pprint

def get_access_token(client_id: str) -> str:
    data = {
        'client_id': client_id,
        "grant_type": "implicit"
    }

    url = 'https://api.moltin.com/oauth/access_token'

    response = requests.get(
        url, data=data
    )
    response.raise_for_status()

    return response.json()['access_token']


def get_products(token: str) -> str:
    headers = {
        "Authorization": f"Bearer {token}",
    }

    url = 'https://api.moltin.com/catalog/products'

    response = requests.get(
        url,
        headers=headers
    )
    response.raise_for_status()

    return response.json()['data']


def get_product(token:str, product_id: str) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
    }

    url = f'https://api.moltin.com/catalog/products/{product_id}'

    response = requests.get(
        url, headers=headers
    )
    response.raise_for_status()

    return response.json()['data']['attributes']


def get_cart_items(token: str, cart_reference: str) -> dict:
    header = {
        "Authorization": f"Bearer {token}",
    }
    url = f"https://api.moltin.com/v2/carts/{cart_reference}/items"
    response = requests.get(url, headers=header)
    response.raise_for_status()

    return response.json()


def add_product(
    token: str,
    cart_reference: str,
    product_id: str,
    quantity: int,
) -> dict:
    header = {
        "Authorization": f"Bearer {token}",
    }
    url = f"https://api.moltin.com/v2/carts/{cart_reference}/items"
    data = {
        "data": {
            "id": product_id,
            "type": "cart_item",
            "quantity": quantity,
        },
    }
    response = requests.post(url, headers=header, json=data)
    response.raise_for_status()

    return response.json()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    elasticpath_client_id = env('ELASTICPATH_CLIENT_ID')
    token = get_access_token(elasticpath_client_id)
    products = get_products(token)
    product_id = products[0]['id']
    pprint(get_product(token, product_id))
    # basket = add_product(token, 'my_cart', product_id, 1)
    # print(basket)
