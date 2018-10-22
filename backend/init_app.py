import os

from flask import Flask
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

db = SQLAlchemy(application)
migrate = Migrate(application, db)
#db.create_all()


from app.resources import ItemsList, Items, CategoryList, Categories, SubcategoryList, Subcategories


api.add_resource(ItemsList, '/api/item')
api.add_resource(Items, '/api/item/<item_id>')
api.add_resource(CategoryList, '/api/category')
api.add_resource(Categories, '/api/category/<category_id>')
api.add_resource(SubcategoryList, '/api/subcategory')
api.add_resource(Subcategories, '/api/subcategory/<subcategory_id>')

if __name__ == '__main__':
    application.run(debug=True)