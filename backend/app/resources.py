from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, \
    get_jwt_identity, get_raw_jwt
from flask_restful import Resource, marshal_with, marshal

from app.marshallers import item_marshaller, category_marshaller, subcategory_marshaller, user_marshaller
from app.models import Item, Category, Subcategory, User, RevokedTokenModel
from app.parsers import item_parser, subcategory_parser, category_parser, creating_item_parser, \
    creating_category_parser, creating_subcategory_parser, user_parser, login_user_parser
from app.repositories import Repository
from init_app import db


def create_tokens(username):
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    return access_token, refresh_token


class Items(Resource):
    @marshal_with(item_marshaller)
    def get(self, item_id):
        return Item.query.get_or_404(item_id)

    @jwt_required
    @marshal_with(item_marshaller)
    def delete(self, item_id):
        item = Item.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return '', 204

    @jwt_required
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

    @jwt_required
    def post(self):
        args = creating_item_parser.parse_args()
        item = Repository.create_and_add(Item, args)
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
        category = Repository.create_and_add(Category, args)
        return marshal(category, category_marshaller), 201


class Subcategories(Resource):
    def get(self, subcategory_id):
        return marshal(Subcategory.query.get_or_404(subcategory_id), subcategory_marshaller)

    @jwt_required
    def delete(self, subcategory_id):
        subcategory = Subcategory.query.get_or_404(subcategory_id)
        db.session.delete(subcategory)
        db.session.commit()
        return marshal('', subcategory_marshaller), 204

    @jwt_required
    def put(self, subcategory_id):
        subcategory = Subcategory.query.get_or_404(subcategory_id)
        args = subcategory_parser.parse_args()
        subcategory.update(args)
        db.session.commit()
        return marshal(subcategory, subcategory_marshaller), 201


class SubcategoryList(Resource):
    def get(self):
        return marshal(Subcategory.query.all(), subcategory_marshaller)

    @jwt_required
    def post(self):
        args = creating_subcategory_parser.parse_args()
        subcategory = Repository.create_and_add(Subcategory, args)
        return marshal(subcategory, subcategory_marshaller), 201


class UserRegistration(Resource):
    def post(self):
        args = user_parser.parse_args()
        new_user = Repository.create_and_add(User, {'username': args['username']})
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
        jwt_id = get_raw_jwt()['jti']
        Repository.create_and_add(RevokedTokenModel, {'jwt_id': jwt_id})
        return {'message': 'Access token has been revoked'}, 201


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jwt_id = get_raw_jwt()['jti']
        Repository.create_and_add(RevokedTokenModel, {'jwt_id': jwt_id})
        return {'message': 'Refresh token has been revoked'}, 201


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    def get(self):
        return marshal(User.query.all(), user_marshaller)
