import os

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from app.exceptions import ApiBaseException

application = Flask(__name__)
api = Api(application)

if application.debug == True:
     application.config.from_object('config.DevelopmentConfig')
else:
    application.config.from_object('config.BaseConfig')

db = SQLAlchemy(application)
migrate = Migrate(application, db)
jwt = JWTManager(application)

from app.models import RevokedTokenModel
from app.resources import ItemsList, Items, CategoryList, Categories, SubcategoryList, Subcategories, \
    UserRegistration, UserLogin, UserLogoutAccess, UserLogoutRefresh, TokenRefresh, AllUsers, BuyItems


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedTokenModel.is_blacklisted(jti)


@application.before_first_request
def create_tables():
    db.create_all()


@application.errorhandler(ApiBaseException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


api.add_resource(ItemsList, '/api/items')
api.add_resource(Items, '/api/items/<item_id>')
api.add_resource(BuyItems, '/api/items/buy')
api.add_resource(CategoryList, '/api/categories')
api.add_resource(Categories, '/api/categories/<category_id>')
api.add_resource(SubcategoryList, '/api/subcategories')
api.add_resource(Subcategories, '/api/subcategories/<subcategory_id>')
api.add_resource(UserRegistration, '/api/registration')
api.add_resource(UserLogin, '/api/login')
api.add_resource(UserLogoutAccess, '/api/logout/access')
api.add_resource(UserLogoutRefresh, '/api/logout/refresh')
api.add_resource(TokenRefresh, '/api/token/refresh')
api.add_resource(AllUsers, '/api/users')

if __name__ == '__main__':
    application.run(debug=True)
