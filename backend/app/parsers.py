from functools import partial

from flask_restful import reqparse

from app.models import Category, Subcategory, Item, User, Role
from init_app import db


def object_exist(model, value, column):
    object_attribute = getattr(model, column)
    return db.session.query(model.query.filter(object_attribute == value).exists()).scalar()


def check_object(model, value, column='name'):
    if not object_exist(model, value, column):
        raise ValueError(f"{value} is not class instance")
    return value


def check_unique_object(model, value, column='name'):
    if object_exist(model, value, column):
        raise ValueError(f"{value} already exist")
    return value


def check_role(value):
    if not (Role.has_value(value)):
        raise ValueError(f"{value} is not a role")
    return value


check_category = partial(check_object, Category, column='name')
check_subcategory = partial(check_object, Subcategory, column='name')
check_unique_item = partial(check_unique_object, Item, column='name')
check_unique_category = partial(check_unique_object, Category, column='name')
check_unique_subcategory = partial(check_unique_object, Subcategory, column='name')
check_unique_user = partial(check_unique_object, User, column='username')

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
subcategory_parser.add_argument('name')
subcategory_parser.add_argument('category', type=check_category)

creating_subcategory_parser = subcategory_parser.copy()
creating_subcategory_parser.replace_argument('name', type=check_unique_subcategory, required=True)

user_parser = reqparse.RequestParser(bundle_errors=True)
user_parser.add_argument('username', required=True, type=check_unique_user)
user_parser.add_argument('password', help='This field cannot be blank', required=True)

login_user_parser = user_parser.copy()
login_user_parser.replace_argument('username', help="This field cannot be blank", required=True)
user_parser.add_argument('roles', type=check_role)
