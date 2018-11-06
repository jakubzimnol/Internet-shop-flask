import os
from json import JSONDecodeError
import json
import requests

from app.exceptions import PayuException
from app.models import Item


def get_access_token():
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    payu_path = os.environ.get('PAYU_PATH')
    payload = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': client_secret}
    path = ''.join((payu_path, 'pl/standard/user/oauth/authorize'))
    #path = 'https://secure.snd.payu.com/standard/user/oauth/authorize'
    response = requests.post(path, params=payload)
    try:
        json = response.json()
        if response.status_code is not 200:
            if json.get('error'):
                raise PayuException(json['error'])
            else:
                raise PayuException()
        return json['access_token']
    except JSONDecodeError:
        raise PayuException()


def create_new_order(items, user, ip, currency_code):
    payu_path = os.environ.get('PAYU_PATH')
    path = ''.join((payu_path, 'api/v2_1/orders'))
    pos_id = os.environ.get('POS_ID')
    payu_token = get_access_token()
    token = ' '.join(('Bearer', payu_token))
    headers = {"Content-Type": "application/json", "Authorization": token}
    # payload = {"notifyUrl": "http://www.localhost:5000",
    #            "customerIp": "127.0.0.1",
    #            "merchantPosId": pos_id,
    #            "description": "RTV market",
    #            "currencyCode": "PLN",
    #            "totalAmount": "21000",
    #            "buyer": {
    #                "email": "john.doe@example.com",
    #                "phone": "654111654",
    #                "firstName": "John",
    #                "lastName": "Doe",
    #                "language": "pl"
    #            },
    #            "settings":{
    #                "invoiceDisabled":"true"
    #             },
    #            "products": [
    #                {
    #                    "name": "Wireless Mouse for Laptop",
    #                    "unitPrice": "15000",
    #                    "quantity": "1"
    #                },
    #                {
    #                    "name": "HDMI cable",
    #                    "unitPrice": "6000",
    #                    "quantity": "1"
    #                }
    #            ]
    #            }
    products = [{"name": item['name'], "unitPrice": item['price'], "quantity": "1"} for item in items]
    total_price = sum([item['price'] for item in items])
    payload = {
        "notifyUrl": "http://www.localhost:5000/api/items/buy",
        "continueUrl": "http://www.localhost:5000/api/items/buy",
        "customerIp": ip,
        "merchantPosId": pos_id,
        "description": "RTV market",
        "currencyCode": currency_code,
        "totalAmount": total_price,
        "buyer": {
                    "email": user.email,
            #        "phone": "654111654",
                    "firstName": user.username,
           #         "lastName": "Doe",
                    "language": "pl"
                },
        "products": products
    }
    response = requests.post(path, headers=headers, json=payload)
    if response.status_code is not 200:
        raise PayuException()
    #print(response.url)
    return response.url
