from flask_restful import reqparse
from sqlalchemy import exists

from app.models import Category, Subcategory
from init_app import db


def is_category(value):
    if not db.session.query(exists().where(Category.name == value)).scalar():
        raise ValueError("Value is not Category")
    return value


def is_subcategory(value):
    if not db.session.query(exists().where(Subcategory.name == value)).scalar():
        raise ValueError("Value is not Subcategory")
    return value


item_parser = reqparse.RequestParser(bundle_errors=True)
item_parser.add_argument('name')
item_parser.add_argument('category', type=is_category, help="This field must be the category")
item_parser.add_argument('subcategory', type=is_subcategory, help="This field must be the subcategory")

creating_item_parser = item_parser.copy()
creating_item_parser.replace_argument('name', required=True, help="This field cannot be left blank")

category_parser = reqparse.RequestParser()
category_parser.add_argument('name')

creating_category_parser = category_parser.copy()
creating_category_parser.replace_argument('name', required=True, help="This field cannot be left blank")

subcategory_parser = reqparse.RequestParser(bundle_errors=True)
subcategory_parser.add_argument('name')
subcategory_parser.add_argument('category', type=is_category, help="This field must be the category")

creating_subcategory_parser = subcategory_parser.copy()
creating_subcategory_parser.replace_argument('name', required=True, help="This field cannot be left blank")
