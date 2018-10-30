from functools import partial

from flask_restful import reqparse

from app.models import Category, Subcategory, Item, User
from init_app import db


def object_exist(model, value, attribute):
    object_attribute = getattr(model, attribute)
    return db.session.query(model.query.filter(object_attribute == value).exists()).scalar()


def check_object(model, value, attribute='name'):
    if not object_exist(model, value, attribute):
        raise ValueError(f"{value} is not class instance")
    return value


def check_unique_object(model, value, attribute='name'):
    if object_exist(model, value, attribute):
        raise ValueError(f"{value} already exist")
    return value


check_category = partial(check_object, Category, attribute='name')


check_subcategory= partial(check_object, Subcategory, attribute='name')


check_unique_item = partial(check_unique_object, Item, attribute='name')


check_unique_category = partial(check_unique_object, Category, attribute='name')


check_unique_subcategory = partial(check_unique_object, Subcategory, attribute='name')


check_unique_user = partial(check_unique_object, User, attribute='username')


item_parser = reqparse.RequestParser(bundle_errors=True)
item_parser.add_argument('name', type=check_unique_item)
item_parser.add_argument('category', type=check_category)
item_parser.add_argument('subcategory', type=check_subcategory)

creating_item_parser = item_parser.copy()
creating_item_parser.replace_argument('name', type=check_unique_item, required=True)

category_parser = reqparse.RequestParser()
category_parser.add_argument('name', type=check_unique_category)

creating_category_parser = category_parser.copy()
creating_category_parser.replace_argument('name', type=check_unique_category, required=True)

subcategory_parser = reqparse.RequestParser(bundle_errors=True)
subcategory_parser.add_argument('name', type=check_unique_subcategory)
subcategory_parser.add_argument('category', type=check_category)

creating_subcategory_parser = subcategory_parser.copy()
creating_subcategory_parser.replace_argument('name', type=check_unique_subcategory, required=True)

user_parser = reqparse.RequestParser(bundle_errors=True)
user_parser.add_argument('username', required=True, type=check_unique_user)
user_parser.add_argument('password', help='This field cannot be blank', required=True)

login_user_parser = user_parser.copy()
login_user_parser.replace_argument('username', help="This field cannot be blank", required=True)
