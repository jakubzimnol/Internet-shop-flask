import os
import unittest

from flask_testing import TestCase

from init_app import application, db
from app.models import User, Item, Category, Subcategory


basedir = os.path.abspath(os.path.dirname(__file__))


class SQLAlchemyTest(TestCase):
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
    TESTING = True

    def create_app(self):
        # pass in test configuration
        return application

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_database(self):
        user = User(username='jakub')
        item = Item(name='item1')
        category = Category(name='category1')
        subcategory = Subcategory(name='subcategory1')
        db.session.add(user)
        db.session.add(item)
        db.session.add(category)
        db.session.add(subcategory)
        db.session.commit()

        assert user in db.session
        assert item in db.session
        assert category in db.session
        assert subcategory in db.session


if __name__ == '__main__':
    unittest.main()
