from flask_restful import fields

item_marshaller = {
    'id': fields.Integer,
    'name': fields.String,
    'category': fields.String,
    'subcategory': fields.String,
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
    'password': fields.String,
}
