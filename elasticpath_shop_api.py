import requests


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

    url = 'https://api.moltin.com/pcm/catalog/products'

    response = requests.get(
        url,
        headers=headers
    )
    response.raise_for_status()

    return response.json()['data']


def get_product(token: str, product_id: str) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
    }

    url = f'https://api.moltin.com/catalog/products/{product_id}'

    response = requests.get(
        url, headers=headers
    )
    response.raise_for_status()

    return response.json()['data']


def get_file_link(token, product_id):
    headers = {
        "Authorization": f"Bearer {token}",
    }
    file_id = get_product(token, product_id)[
        'relationships']['main_image']['data']['id']
    url = f'https://api.moltin.com/v2/files/{file_id}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()['data']['link']['href']


def get_cart(token: str, cart_reference: str) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
    }
    url = f"https://api.moltin.com/v2/carts/{cart_reference}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def get_cart_items(token: str, cart_reference: str) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
    }
    url = f"https://api.moltin.com/v2/carts/{cart_reference}/items"
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def remove_cart_item(token: str, cart_reference: str, item_id: str,) -> None:
    headers = {
        "Authorization": f"Bearer {token}",
    }
    url = f"https://api.moltin.com/v2/carts/{cart_reference}/items/{item_id}"
    response = requests.delete(url, headers=headers)
    response.raise_for_status()


def add_product(token: str, cart_reference: str, product_id: str, quantity: int,) -> dict:
    headers = {
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
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()


def create_customer(token: str, name: str, email: str,) -> str:
    headers = {
        "Authorization": f"Bearer {token}",
    }
    url = f"https://api.moltin.com/v2/customers"
    data = {
        "data": {
            "type": "customer",
            "name": name,
            "email": email,
        },
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()


def get_customer(token: str, id: str) -> str:
    headers = {
        "Authorization": f"Bearer {token}",
    }
    url = f"https://api.moltin.com/v2/customers/{id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()
