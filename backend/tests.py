import unittest

from flask import json
from flask_jwt_extended import create_access_token
from flask_testing import TestCase


from init_app import db, application
from app.models import User, Item, Category, Subcategory
from app.repositories import Repository


class BaseTestCaseClass(TestCase):
    def create_app(self):
        application.config.from_object('config.TestingConfig')
        return application

    def setUp(self):
        db.session.remove()
        db.drop_all()
        db.create_all()
        self.buyer = Repository.create_and_add(User, {'username': 'buyer', 'roles': 'Buyer'})
        self.seller = Repository.create_and_add(User, {'username': 'seller', 'roles': 'Seller'})
        self.admin = Repository.create_and_add(User, {'username': 'admin', 'roles': 'Admin'})
        self.item = Repository.create_and_add(Item, {'name': 'item1'})
        self.category = Repository.create_and_add(Category, {'name': 'category1'})
        self.subcategory = Repository.create_and_add(Subcategory, {'name': 'subcategory1'})
        self.new_name = "new_name"
        self.update_item_dict = {
            'name': self.new_name,
            'category': self.category.name,
            'subcategory': self.subcategory.name,
                       }
        self.update_category_dict = {'name': 'category2'}
        self.update_subcategory_dict = {'name': 'subcategory2'}
        self.new_user_dict = {'username': 'newuser', 'password': 'newpassword'}
        self.buyer_access_token = create_access_token(self.buyer.username)
        self.buyer_headers = {'Authorization': 'Bearer {}'.format(self.buyer_access_token)}
        self.seller_access_token = create_access_token(self.seller.username)
        self.seller_headers = {'Authorization': 'Bearer {}'.format(self.seller_access_token)}
        self.admin_access_token = create_access_token(self.admin.username)
        self.admin_headers = {'Authorization': 'Bearer {}'.format(self.admin_access_token)}

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class SQLAlchemyTest(BaseTestCaseClass):

    def test_item_update(self):
        self.item.update(self.update_item_dict)
        assert self.new_name in self.item.name
        assert self.category is self.item.category
        assert self.subcategory is self.item.subcategory

    def test_get_updated_item(self):
        self.item.update(self.update_item_dict)
        response = self.client.get("/api/items", headers=self.buyer_headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)[0]
        assert self.new_name in data['name']
        assert self.category.name in data['category']
        assert self.subcategory.name in data['subcategory']


class AuthorizationTestCase(BaseTestCaseClass):

    def check_role(self, method, url, data, headers, status_code):
        self.setUp()
        response = method(url, data=data, headers=headers)
        self.assertEqual(response.status_code, status_code)
        self.tearDown()

    def check_roles_authentication(self, method, url, data, buyer_status_code,
                                   seller_status_code, admin_status_code, unauthorized_status_code=401):
        self.check_role(method, url, data, self.buyer_headers, buyer_status_code)
        self.check_role(method, url, data, self.seller_headers, seller_status_code)
        self.check_role(method, url, data, self.admin_headers, admin_status_code)
        self.check_role(method, url, data, [], unauthorized_status_code)

    def test_items_get(self):
        self.check_roles_authentication(method=self.client.get,
                                        url="/api/items",
                                        data={},
                                        buyer_status_code=200,
                                        seller_status_code=200,
                                        admin_status_code=200)

    def test_items_post(self):
        self.check_roles_authentication(method=self.client.post,
                                        url="/api/items",
                                        data=self.update_item_dict,
                                        buyer_status_code=401,
                                        seller_status_code=201,
                                        admin_status_code=201)

    def test_item_put(self):
        self.check_roles_authentication(method=self.client.put,
                                        url="/api/items/1",
                                        data=self.update_item_dict,
                                        buyer_status_code=401,
                                        seller_status_code=201,
                                        admin_status_code=201)

    def test_item_delete(self):
        self.check_roles_authentication(method=self.client.delete,
                                        url="/api/items/1",
                                        data={},
                                        buyer_status_code=401,
                                        seller_status_code=204,
                                        admin_status_code=204)

    def test_item_get(self):
        self.check_roles_authentication(method=self.client.get,
                                        url="/api/items/1",
                                        data={},
                                        buyer_status_code=200,
                                        seller_status_code=200,
                                        admin_status_code=200)

    def test_categories_get(self):
        self.check_roles_authentication(method=self.client.get,
                                        url="/api/categories",
                                        data={},
                                        buyer_status_code=200,
                                        seller_status_code=200,
                                        admin_status_code=200)

    def test_categories_post(self):
        self.check_roles_authentication(method=self.client.post,
                                        url="/api/categories",
                                        data=self.update_category_dict,
                                        buyer_status_code=401,
                                        seller_status_code=401,
                                        admin_status_code=201)

    def test_category_put(self):
        self.check_roles_authentication(method=self.client.put,
                                        url="/api/categories/1",
                                        data=self.update_category_dict,
                                        buyer_status_code=401,
                                        seller_status_code=401,
                                        admin_status_code=201)

    def test_category_delete(self):
        self.check_roles_authentication(method=self.client.delete,
                                        url="/api/categories/1",
                                        data={},
                                        buyer_status_code=401,
                                        seller_status_code=401,
                                        admin_status_code=204)

    def test_category_get(self):
        self.check_roles_authentication(method=self.client.get,
                                        url="/api/categories/1",
                                        data={},
                                        buyer_status_code=200,
                                        seller_status_code=200,
                                        admin_status_code=200)

    def test_subcategories_get(self):
        self.check_roles_authentication(method=self.client.get,
                                        url="/api/subcategories",
                                        data={},
                                        buyer_status_code=200,
                                        seller_status_code=200,
                                        admin_status_code=200)

    def test_subcategories_post(self):
        self.check_roles_authentication(method=self.client.post,
                                        url="/api/subcategories",
                                        data=self.update_subcategory_dict,
                                        buyer_status_code=401,
                                        seller_status_code=401,
                                        admin_status_code=201)

    def test_subcategory_put(self):
        self.check_roles_authentication(method=self.client.put,
                                        url="/api/subcategories/1",
                                        data=self.update_subcategory_dict,
                                        buyer_status_code=401,
                                        seller_status_code=401,
                                        admin_status_code=201)

    def test_subcategory_delete(self):
        self.check_roles_authentication(method=self.client.delete,
                                        url="/api/subcategories/1",
                                        data={},
                                        buyer_status_code=401,
                                        seller_status_code=401,
                                        admin_status_code=204)

    def test_subcategory_get(self):
        self.check_roles_authentication(method=self.client.get,
                                        url="/api/subcategories/1",
                                        data={},
                                        buyer_status_code=200,
                                        seller_status_code=200,
                                        admin_status_code=200)

    def test_users_get(self):
        self.check_roles_authentication(method=self.client.get,
                                        url="/api/users",
                                        data={},
                                        buyer_status_code=401,
                                        seller_status_code=401,
                                        admin_status_code=200,
                                        )

    def test_users_post(self):
        self.check_roles_authentication(method=self.client.post,
                                        url="/api/registration",
                                        data=self.new_user_dict,
                                        buyer_status_code=201,
                                        seller_status_code=201,
                                        admin_status_code=201,
                                        unauthorized_status_code=201)


if __name__ == '__main__':
    unittest.main()
