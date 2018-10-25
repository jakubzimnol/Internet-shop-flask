from flask_restful import Resource, marshal_with, marshal

from app.marshallers import item_marshaller, category_marshaller, subcategory_marshaller, user_marshaller
from app.models import Item, Category, Subcategory, User
from app.parsers import item_parser, subcategory_parser, category_parser, creating_item_parser, \
    creating_category_parser, creating_subcategory_parser, user_parser
from app.repositories import Repository
from init_app import db
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)


class Items(Resource):
    @marshal_with(item_marshaller)
    def get(self, item_id):
        return Item.query.get_or_404(item_id)

    @marshal_with(item_marshaller)
    def delete(self, item_id):
        item = Item.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return '', 204

    @marshal_with(item_marshaller)
    def put(self, item_id):
        item = Item.query.get_or_404(item_id)
        args = item_parser.parse_args()
        item.update(args)
        db.session.commit()
        return item, 201


class ItemsList(Resource):
    def get(self):
        return marshal(Item.query.all(), item_marshaller)

    def post(self):
        args = creating_item_parser.parse_args()
        item = Item(name=args['name'])
        if not Repository.add_to_database(item):
            return 404
        item.update(args)
        db.session.commit()
        return marshal(item, item_marshaller), 201


class Categories(Resource):
    def get(self, category_id):
        return marshal(Category.query.get_or_404(category_id), category_marshaller)

    @jwt_required
    def delete(self, category_id):
        item = Category.query.get_or_404(category_id)
        db.session.delete(item)
        db.session.commit()
        return marshal('', category_marshaller), 204

    @jwt_required
    def put(self, category_id):
        category = Category.query.get_or_404(category_id)
        args = category_parser.parse_args()
        category.update(args)
        db.session.commit()
        return marshal(category, category_marshaller), 201


class CategoryList(Resource):
    def get(self):
        return marshal(Category.query.all(), category_marshaller)

    @jwt_required
    def post(self):
        args = creating_category_parser.parse_args()
        category = Category(name=args['name'])
        if not Repository.add_to_database(category):
            return 404
        return marshal(category, category_marshaller), 201


class Subcategories(Resource):
    def get(self, subcategory_id):
        return marshal(Subcategory.query.get_or_404(subcategory_id), subcategory_marshaller)

    def delete(self, subcategory_id):
        subcategory = Subcategory.query.get_or_404(subcategory_id)
        db.session.delete(subcategory)
        db.session.commit()
        return marshal('', subcategory_marshaller), 204

    def put(self, subcategory_id):
        subcategory = Subcategory.query.get_or_404(subcategory_id)
        args = subcategory_parser.parse_args()
        subcategory.update(args)
        db.session.commit()
        return marshal(subcategory, subcategory_marshaller), 201


class SubcategoryList(Resource):
    def get(self):
        return marshal(Subcategory.query.all(), subcategory_marshaller)

    def post(self):
        args = creating_subcategory_parser.parse_args()
        subcategory = Subcategory(name=args['name'])
        if not Repository.add_to_database(subcategory):
            return 404
        return marshal(subcategory, subcategory_marshaller), 201


class UserRegistration(Resource):
    def post(self):
        args = user_parser.parse_args()
        new_user = User(
            username=args['username'],
            password_hash=args['password']
        )
        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=args['username'])
            refresh_token = create_refresh_token(identity=args['username'])
            return {
                'message': 'User {} was created'.format(args['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except:
            return {'message': 'Something went wrong'}, 500

        # if not Repository.add_to_database(new_user):
        #     return 404
        # return marshal(new_user, user_marshaller), 201


class UserLogin(Resource):
    def post(self):
        args = user_parser.parse_args()
        current_user = User.query.filter_by(username=args['username']).first_or_404()
        if current_user.check_password(args['password']):
            access_token = create_access_token(identity=args['username'])
            refresh_token = create_refresh_token(identity=args['username'])
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': 'Wrong credentials'}


class UserLogoutAccess(Resource):
    def post(self):
        return {'message': 'User logout'}


class UserLogoutRefresh(Resource):
    def post(self):
        return {'message': 'User logout'}


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    def get(self):
        return marshal(User.query.all(), user_marshaller)

    def delete(self):
        users = User.query.all()
        db.session.delete(users)
        db.session.commit()
        return marshal(users, user_marshaller), 204


class SecretResource(Resource):
    def get(self):
        return {
            'answer': 42
        }
