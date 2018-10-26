import os
import unittest

from flask import json
from flask_testing import TestCase

from init_app import application, db
from app.models import User, Item, Category, Subcategory


basedir = os.path.abspath(os.path.dirname(__file__))


class SQLAlchemyTest(TestCase):
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
    TESTING = True

    def create_app(self):
        # pass in test configuration
        return application

    def setUp(self):
        db.create_all()
        self.user = User(username='jakub')
        self.item = Item(name='item1')
        self.category = Category(name='category1')
        self.subcategory = Subcategory(name='subcategory1')
        db.session.add(self.user)
        db.session.add(self.item)
        db.session.add(self.category)
        db.session.add(self.subcategory)
        db.session.commit()
        self.new_name = "new_name"
        self.update_item_dict = {
            'name': self.new_name,
            'category': self.category.name,
            'subcategory': self.subcategory.name,
                       }

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_item_update(self):
        self.item.update_item(self.update_item_dict)
        assert self.new_name in self.item.name
        assert self.category in self.item.category
        assert self.subcategory in self.item.subcategory

    def test_get_item(self):
        self.item.update_item(self.update_item_dict)
        response = self.client.get("/api/item")
        data = json.loads(response.data)[0]
        assert self.new_name in data['name']
        assert self.category.name in data['category']
        assert self.subcategory.name in data['subcategory']


if __name__ == '__main__':
    unittest.main()
