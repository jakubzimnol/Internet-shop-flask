import os
from json import JSONDecodeError

import requests
from flask import json

from app.exceptions import PayuException, BadContentInResponse, NoPermissionException
from app.models import Order
from init_app import db
import hashlib


def get_access_token():
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    payu_path = os.environ.get('PAYU_PATH')
    payload = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': client_secret}
    path = ''.join((payu_path, 'pl/standard/user/oauth/authorize'))
    response = requests.post(path, params=payload)
    try:
        json_dict = response.json()
        if response.status_code is not 200:
            if json_dict.get('error'):
                raise PayuException(json_dict['error'])
            else:
                raise PayuException()
        return json_dict['access_token']
    except JSONDecodeError:
        raise PayuException()


def get_products_list(order):
    return [{"name": ordered_item.item.name, "unitPrice": ordered_item.item.price, "quantity": "1"}
                for ordered_item in order.ordered_items]


def get_total_price(order):
    return sum([ordered_item.item.price for ordered_item in order.ordered_items])


def create_order_payload(order, url_root, currency_code, ip, language):
    products = get_products_list(order)
    total_price = get_total_price(order)
    return {
        "notifyUrl": f"{url_root}api/items/notify",
        "continueUrl": f"{url_root}api/orders/{order.id}",
        "customerIp": ip,
        "merchantPosId": os.environ.get('POS_ID'),
        "description": order.description,
        "currencyCode": currency_code,
        "totalAmount": total_price,
        "buyer": {
            "email": order.buyer.email,
            "firstName": order.buyer.username,
            "language": language,
        },
        "products": products
    }


def get_order_headers():
    token = ' '.join(('Bearer', get_access_token()))
    return {"Content-Type": "application/json", "Authorization": token}


def set_payu_order_id(order, payu_order_id):
    order.payu_order_id = payu_order_id
    db.session.commit()


def send_new_order_to_payu(order_id, ip, currency_code, url_root, language):
    path = ''.join((os.environ.get('PAYU_PATH'), 'api/v2_1/orders'))
    headers = get_order_headers()
    order = db.session.query(Order).get(order_id)
    payload = create_order_payload(order, url_root, currency_code, ip, language)
    response = requests.post(path, headers=headers, json=payload, allow_redirects=False)
    if response.status_code != 302:
        raise PayuException()
    json = response.json()
    set_payu_order_id(order, json['orderId'])
    return json['redirectUri']


def get_signature(open_payu_header):
    result1 = open_payu_header.split('signature=')
    result2 = result1[1].split(';')
    return result2[0]


def verify_notification(headers, json_dict):
    open_payu_header = headers.get('OpenPayu-Signature')
    if not open_payu_header:
        raise NoPermissionException
    signature = get_signature(open_payu_header)
    joined_str = json.dumps(json_dict) + os.environ.get('MD5')
    expected_signature = hashlib.md5(joined_str.encode("utf-8")).hexdigest()
    if expected_signature != signature:
        raise NoPermissionException


def set_order_status(args):
    order = args.get('order')
    if not order:
        raise BadContentInResponse
    payu_order_id = order.get('orderId')
    status = order.get('status')
    order = db.session.query(Order).filter_by(payu_order_id=payu_order_id).first_or_404()
    order.status = status
    db.session.commit()
