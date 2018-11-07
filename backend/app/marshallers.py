from flask_restful import fields

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

order_marshaller = {
    'id': fields.Integer,
     #'items': fields.list,
    'description': fields.String,
    'payu_order_id': fields.String,
    'status': fields.String,
    'payment_status': fields.String
}
