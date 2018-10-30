from flask_restful import reqparse

from app.models import Category, Subcategory, Item, User, Role
from init_app import db


def object_exist(model, value, name):
    object_attribute = getattr(model, name)
    return db.session.query(model.query.filter(object_attribute == value).exists()).scalar()


def check_object(model, value, name='name'):
    if not object_exist(model, value, name):
        raise ValueError(f"{value} is not class instance")
    return value


def check_unique_object(model, value, name='name'):
    if object_exist(model, value, name):
        raise ValueError(f"{value} already exist")
    return value


def check_category(value):
    return check_object(Category, value)


def check_role(value):
    if not (Role.has_value(value)):
        raise ValueError(f"{value} is not a role")
    return value


def check_subcategory(value):
    return check_object(Subcategory, value)


def check_unique_item(value):
    return check_unique_object(Item, value)


def check_unique_category(value):
    return check_unique_object(Category, value)


def check_unique_subcategory(value):
    return check_unique_object(Subcategory, value)


def check_unique_user(value):
    return check_unique_object(User, value, 'username')


item_parser = reqparse.RequestParser(bundle_errors=True)
item_parser.add_argument('name', type=check_unique_item, help="That name already exist")
item_parser.add_argument('category', type=check_category)
item_parser.add_argument('subcategory', type=check_subcategory)

creating_item_parser = item_parser.copy()
creating_item_parser.replace_argument('name', type=check_unique_item,
                                      required=True, help="Name must be unique")

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
user_parser.add_argument('username', help="Username must be unique", required=True, type=check_unique_user)
user_parser.add_argument('password', help='This field cannot be blank', required=True)

login_user_parser = user_parser.copy()
login_user_parser.replace_argument('username', help="This field cannot be blank", required=True)
user_parser.add_argument('roles', type=check_role)
