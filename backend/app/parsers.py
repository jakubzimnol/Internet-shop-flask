from flask_restful import reqparse
from sqlalchemy import exists

from app.models import Category, Subcategory, Item, User
from init_app import db


def check_category(value):
    if not db.session.query(exists().where(Category.name == value)).scalar():
        raise ValueError("Value is not Category instance")
    return value


def check_subcategory(value):
    if not db.session.query(exists().where(Subcategory.name == value)).scalar():
        raise ValueError("Value is not Subcategory instance")
    return value


def check_unique_item(value):
    if db.session.query(exists().where(Item.name == value)).scalar():
        raise ValueError("Value already exist")
    return value


def check_unique_category(value):
    if db.session.query(exists().where(Category.name == value)).scalar():
        raise ValueError("Value already exist")
    return value


def check_unique_subcategory(value):
    if db.session.query(exists().where(Subcategory.name == value)).scalar():
        raise ValueError("Value already exist")
    return value


def check_unique_user(value):
    if db.session.query(exists().where(User.username == value)).scalar():
        raise ValueError("Value already exist")
    return value


item_parser = reqparse.RequestParser(bundle_errors=True)
item_parser.add_argument('name', type=check_unique_item, help="That name already exist")
item_parser.add_argument('category', type=check_category, help="This field must be the Category instance")
item_parser.add_argument('subcategory', type=check_subcategory, help="This field must be the Subcategory instance")

creating_item_parser = item_parser.copy()
creating_item_parser.replace_argument('name', type=check_unique_item,
                                      required=True, help="Name must be unique")

category_parser = reqparse.RequestParser()
category_parser.add_argument('name', type=check_unique_category, help="That category already exist")

creating_category_parser = category_parser.copy()
creating_category_parser.replace_argument('name', type=check_unique_category,
                                          required=True, help="Name must be unique")

subcategory_parser = reqparse.RequestParser(bundle_errors=True)
subcategory_parser.add_argument('name', type=check_unique_subcategory, help="That subcategory already exist")
subcategory_parser.add_argument('category', type=check_category, help="Name must be unique")

creating_subcategory_parser = subcategory_parser.copy()
creating_subcategory_parser.replace_argument('name', type=check_unique_subcategory,
                                             required=True, help="Name must be unique")

user_parser = reqparse.RequestParser(bundle_errors=True)
user_parser.add_argument('username', help="Username must be unique", required=True, type=check_unique_user)
user_parser.add_argument('password', help='This field cannot be blank', required=True)
