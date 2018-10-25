import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

application = Flask(__name__)
api = Api(application)

basedir = os.path.abspath(os.path.dirname(__file__))
if application.debug == True:
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
else:
    application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
application.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
application.config['JWT_BLACKLIST_ENABLED'] = True
application.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

db = SQLAlchemy(application)
migrate = Migrate(application, db)
jwt = JWTManager(application)

from app.models import RevokedTokenModel
import app.resources as resources


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedTokenModel.is_jti_blacklisted(jti)


@application.before_first_request
def create_tables():
    db.create_all()


api.add_resource(resources.ItemsList, '/api/item')
api.add_resource(resources.Items, '/api/item/<item_id>')
api.add_resource(resources.CategoryList, '/api/category')
api.add_resource(resources.Categories, '/api/category/<category_id>')
api.add_resource(resources.SubcategoryList, '/api/subcategory')
api.add_resource(resources.Subcategories, '/api/subcategory/<subcategory_id>')
api.add_resource(resources.UserRegistration, '/api/registration')
api.add_resource(resources.UserLogin, '/api/login')
api.add_resource(resources.UserLogoutAccess, '/api/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/api/logout/refresh')
api.add_resource(resources.TokenRefresh, '/api/token/refresh')
api.add_resource(resources.AllUsers, '/api/users')

if __name__ == '__main__':
    application.run(debug=True)
