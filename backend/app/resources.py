from flask import redirect, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, \
    get_jwt_identity, get_raw_jwt
from flask_restful import Resource, marshal_with, marshal

from app.marshallers import item_marshaller, category_marshaller, subcategory_marshaller, user_marshaller
from app.models import Item, Category, Subcategory, User, RevokedTokenModel, Role
from app.parsers import item_parser, subcategory_parser, category_parser, creating_item_parser, \
    creating_category_parser, creating_subcategory_parser, user_parser, login_user_parser, buyer_items_parser, \
    root_items_parser
from app.repositories import Repository
from app.services import create_new_order
from init_app import db


def create_tokens(username):
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    return access_token, refresh_token


def roles_required(role):
    def wrapper(func):
        def check_role_and_call(*args, **kwargs):
            if Repository.is_admin_role() or Repository.check_role(role):
                return func(*args, **kwargs)
            return {'message': 'No permission!'}, 401
        return check_role_and_call
    return wrapper


class BuyItems(Resource):
    # @jwt_required
    # @roles_required([Role.BUYER, Role.SELLER])
    def post(self):
        args = root_items_parser.parse_args()
        items = args['items']
        #user = Repository.get_logged_user()
        user = User.query.get(1)
        ip = request.remote_addr
        currency_code = "PLN"
        return redirect(create_new_order(items, user, ip, currency_code), 302)


class Items(Resource):

    # @jwt_required
    # @roles_required([Role.BUYER, Role.SELLER])
    @marshal_with(item_marshaller)
    def get(self, item_id):
        return Item.query.get_or_404(item_id)

    @jwt_required
    @roles_required([Role.SELLER])
    @marshal_with(item_marshaller)
    def delete(self, item_id):
        item = Item.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return '', 204

    @jwt_required
    @roles_required([Role.SELLER])
    @marshal_with(item_marshaller)
    def put(self, item_id):
        item = Item.query.get_or_404(item_id)
        args = item_parser.parse_args()
        item.update(args)
        db.session.commit()
        return item, 201


class ItemsList(Resource):
    @jwt_required
    @roles_required([Role.BUYER, Role.SELLER])
    def get(self):
        return marshal(Item.query.all(), item_marshaller)

    @jwt_required
    @roles_required([Role.SELLER])
    def post(self):
        args = creating_item_parser.parse_args()
        item = Repository.create_and_add(Item, args)
        return marshal(item, item_marshaller), 201


class Categories(Resource):
    @jwt_required
    @roles_required([Role.BUYER, Role.SELLER])
    def get(self, category_id):
        return marshal(Category.query.get_or_404(category_id), category_marshaller)

    @jwt_required
    @roles_required([Role.SELLER])
    def delete(self, category_id):
        item = Category.query.get_or_404(category_id)
        db.session.delete(item)
        db.session.commit()
        return marshal('', category_marshaller), 204

    @jwt_required
    @roles_required([Role.SELLER])
    def put(self, category_id):
        category = Category.query.get_or_404(category_id)
        args = category_parser.parse_args()
        category.update(args)
        db.session.commit()
        return marshal(category, category_marshaller), 201


class CategoryList(Resource):
    @jwt_required
    @roles_required([Role.BUYER, Role.SELLER])
    def get(self):
        return marshal(Category.query.all(), category_marshaller)

    @jwt_required
    @roles_required([Role.SELLER])
    def post(self):
        args = creating_category_parser.parse_args()
        category = Repository.create_and_add(Category, args)
        return marshal(category, category_marshaller), 201


class Subcategories(Resource):
    @jwt_required
    @roles_required([Role.BUYER, Role.SELLER])
    def get(self, subcategory_id):
        return marshal(Subcategory.query.get_or_404(subcategory_id), subcategory_marshaller)

    @jwt_required
    @roles_required([Role.SELLER])
    def delete(self, subcategory_id):
        subcategory = Subcategory.query.get_or_404(subcategory_id)
        db.session.delete(subcategory)
        db.session.commit()
        return marshal('', subcategory_marshaller), 204

    @jwt_required
    @roles_required([Role.SELLER])
    def put(self, subcategory_id):
        subcategory = Subcategory.query.get_or_404(subcategory_id)
        args = subcategory_parser.parse_args()
        subcategory.update(args)
        db.session.commit()
        return marshal(subcategory, subcategory_marshaller), 201


class SubcategoryList(Resource):
    @jwt_required
    @roles_required([Role.BUYER, Role.SELLER])
    def get(self):
        return marshal(Subcategory.query.all(), subcategory_marshaller)

    @jwt_required
    @roles_required([Role.SELLER])
    def post(self):
        args = creating_subcategory_parser.parse_args()
        subcategory = Repository.create_and_add(Subcategory, args)
        return marshal(subcategory, subcategory_marshaller), 201


class UserRegistration(Resource):
    def post(self):
        args = user_parser.parse_args()
        copy_args = args.copy()
        del copy_args['password']
        new_user = Repository.create_and_add(User, copy_args)
        new_user.password_hash = args['password']
        db.session.commit()
        access_token, refresh_token = create_tokens(args['username'])
        return {
                   'message': f"User {args['username']} was created",
                   'access_token': access_token,
                   'refresh_token': refresh_token
               }, 201


class UserLogin(Resource):
    def post(self):
        args = login_user_parser.parse_args()
        current_user = User.query.filter_by(username=args['username']).first_or_404()
        if current_user.check_password(args['password']):
            access_token, refresh_token = create_tokens(args['username'])
            return {
                'message': f'Logged in as {current_user.username}',
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        return {'message': 'Wrong credentials'}


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jwi = get_raw_jwt()['jti']
        Repository.create_and_add(RevokedTokenModel, {'jwi': jwi})
        return {'message': 'Access token has been revoked'}, 201


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jwi = get_raw_jwt()['jti']
        Repository.create_and_add(RevokedTokenModel, {'jwi': jwi})
        return {'message': 'Refresh token has been revoked'}, 201


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    @jwt_required
    @roles_required([Role.ADMIN])
    def get(self):
        return marshal(User.query.all(), user_marshaller)
