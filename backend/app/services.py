import hashlib
import os
from json import JSONDecodeError

import requests
from flask import json

from app.exceptions import PayuException, BadContentInResponse, NoPermissionException, IntegrityException
from app.models import Order, PayuStatus, Status, OrderedItem
from app.repositories import Repository
from init_app import db


class PayuSender:
    @classmethod
    def get_access_token(cls):
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

    @staticmethod
    def get_products_list(order):
        return [{"name": ordered_item.item.name, "unitPrice": ordered_item.item.price, "quantity": "1"}
                for ordered_item in order.ordered_items]

    @staticmethod
    def get_total_price(order):
        return sum([ordered_item.item.price for ordered_item in order.ordered_items])

    @classmethod
    def create_order_payload(cls, order, url_root, currency_code, ip, language):
        products = cls.get_products_list(order)
        total_price = cls.get_total_price(order)
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

    @classmethod
    def get_order_headers(cls):
        token = ' '.join(('Bearer', cls.get_access_token()))
        return {"Content-Type": "application/json", "Authorization": token}

    @staticmethod
    def set_payu_order_id(order, payu_order_id):
        order.payu_order_id = payu_order_id
        db.session.commit()

    @classmethod
    def send_new_order_to_payu(cls, order, ip, currency_code, url_root, language):
        path = ''.join((os.environ.get('PAYU_PATH'), 'api/v2_1/orders'))
        headers = cls.get_order_headers()
        payload = cls.create_order_payload(order, url_root, currency_code, ip, language)
        response = requests.post(path, headers=headers, json=payload, allow_redirects=False)
        if response.status_code != 302:
            raise PayuException()
        json = response.json()
        cls.set_payu_order_id(order, json['orderId'])
        return json['redirectUri']


class NotificationReceiver:
    @staticmethod
    def get_signature(open_payu_header):
        result1 = open_payu_header.split('signature=')
        result2 = result1[1].split(';')
        return result2[0]

    @classmethod
    def verify_notification(cls, headers, json_dict):
        open_payu_header = headers.get('OpenPayu-Signature')
        if not open_payu_header:
            raise NoPermissionException
        signature = cls.get_signature(open_payu_header)
        joined_str = json.dumps(json_dict) + os.environ.get('MD5')
        expected_signature = hashlib.md5(joined_str.encode("utf-8")).hexdigest()
        if expected_signature != signature:
            raise NoPermissionException

    @staticmethod
    def do_nothing(order):
        pass

    @staticmethod
    def set_status_canceled(order):
        OrderCreator.increase_items_amount(order.ordered_items)
        order.status = Status.CANCELED

    @staticmethod
    def set_status_paid(order):
        order.status = Status.PAID
        db.session.commit()

    status_action = {
        PayuStatus.PENDING.value: do_nothing,
        PayuStatus.CANCELED.value: set_status_canceled,
        PayuStatus.COMPLETED.value: set_status_paid,
        PayuStatus.REJECTED.value: set_status_canceled,
    }

    @classmethod
    def set_order_payment_status(cls, args):
        order = args.get('order')
        if not order:
            raise BadContentInResponse
        payu_order_id = order.get('orderId')
        payment_status = order.get('status')
        order = db.session.query(Order).filter_by(payu_order_id=payu_order_id).first_or_404()
        order.payment_status = payment_status
        db.session.commit()
        cls.status_action[payment_status](order)


class OrderCreator:
    @staticmethod
    def add_key_to_each_dict(dict_list, key, value):
        for dictionary in dict_list:
            dictionary[key] = value
        return dict_list

    @staticmethod
    def decrease_items_amount(ordered_items):
        for ordered_item in ordered_items:
            ordered_item.item.amount -= ordered_item.quantity
            if ordered_item.item.amount < 0:
                db.session.rollback()
                raise IntegrityException()
        db.session.commit()

    @staticmethod
    def increase_items_amount(ordered_items):
        for ordered_item in ordered_items:
            ordered_item.item.amount += ordered_item.quantity
        db.session.commit()

    @classmethod
    def create_order(cls, args, user):
        items_dict = args['items']
        order_dict = {'description': args['description'], 'buyer': user}
        new_order = Repository.create_and_add(Order, order_dict)
        order_id = new_order.id
        cls.add_key_to_each_dict(items_dict, 'order_id', order_id)
        ordered_items = Repository.create_and_add_objects_list(OrderedItem, items_dict)
        cls.decrease_items_amount(ordered_items)
        return new_order
