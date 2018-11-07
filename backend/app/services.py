import os
from json import JSONDecodeError

import requests

from app.exceptions import PayuException, BadContentInResponse
from app.models import Order
from init_app import db


def get_access_token():
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    payu_path = os.environ.get('PAYU_PATH')
    payload = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': client_secret}
    path = ''.join((payu_path, 'pl/standard/user/oauth/authorize'))
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


def create_new_order(order_id, ip, currency_code, url_root):
    payu_path = os.environ.get('PAYU_PATH')
    path = ''.join((payu_path, 'api/v2_1/orders'))
    pos_id = os.environ.get('POS_ID')
    payu_token = get_access_token()
    token = ' '.join(('Bearer', payu_token))
    headers = {"Content-Type": "application/json", "Authorization": token}
    order = db.session.query(Order).get(order_id)
    products = [{"name": ordered_item.item.name, "unitPrice": ordered_item.item.price, "quantity": "1"}
                for ordered_item in order.ordered_items]
    total_price = sum([ordered_item.item.price for ordered_item in order.ordered_items])
    payload = {
        "notifyUrl": f"{url_root}api/items/notify",
        "continueUrl": f"{url_root}api/orders/{order_id}",
        "customerIp": ip,
        "merchantPosId": pos_id,
        "description": order.description,
        "currencyCode": currency_code,
        "totalAmount": total_price,
        "buyer": {
                    "email": order.buyer.email,
            #        "phone": "654111654",
                    "firstName": order.buyer.username,
           #         "lastName": "Doe",
                    "language": "pl"
                },
        "products": products
    }
    response = requests.post(path, headers=headers, json=payload, allow_redirects=False)
    if response.status_code != 302:
        raise PayuException()
    json = response.json()
    order.payu_order_id = json['orderId']
    db.session.commit()
    return json['redirectUri']


def verify_notification(headers, json):
    signature_header = headers.get['OpenPayu-Signature']
    signature = signature_header['signature']
    concatenated = json + os.environ.get('MD5')
    expected_signature = md5(concatenated)
    if expected_signature !=signature:
        raise AuthorizationException



def set_order_status(args):
    order = args.get('order')
    if not order:
        raise BadContentInResponse
    order_id = order.get('orderId')
    status = order.get('status')
    order = db.session.query(Order).filter_by(order_id=order_id)
    order.status = status
