from flask_restful import fields, marshal

item_marshaller = {
    'id': fields.Integer,
    'name': fields.String,
    'category': fields.String,
    'subcategory': fields.String,
    'price': fields.Integer,
    'amount': fields.Integer
}

category_marshaller = {
    'id': fields.Integer,
    'name': fields.String,
}

subcategory_marshaller = {
    'id': fields.Integer,
    'name': fields.String,
    'category': fields.String,
}

user_marshaller = {
    'username': fields.String,
    'roles': fields.String,
}


class OrderItemMarshaller(fields.Raw):
    def format(self, item):
        return marshal(item, item_marshaller)


order_item_marshaller = {
    'id': fields.Integer,
    'item': OrderItemMarshaller,
    'quantity': fields.Integer
}


class OrderItemsMarshaller(fields.Raw):
    def format(self, ordered_items):
        return [marshal(order_item, order_item_marshaller) for order_item in ordered_items]


order_marshaller = {
    'id': fields.Integer,
    'ordered_items': OrderItemsMarshaller,
    'description': fields.String,
    'payu_order_id': fields.String,
    'status': fields.String,
    'payment_status': fields.String
}
