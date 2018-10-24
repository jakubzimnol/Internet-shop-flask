import enum

from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

from init_app import db
from abc import ABC, abstractmethod


class ObjectABC(ABC):
    name = db.Column(db.String(80), unique=True, nullable=False)
    @abstractmethod
    def update(self, parameters):
        if parameters.get('name'):
            self.name = parameters['name']



class Role(enum.Enum):
    ADMIN = "Admin"
    SELLER = "Seller"
    BUYER = "Buyer"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    _password_hash = db.Column(db.String(128))
    sold_item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    bought_item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    sold_item = db.relationship('Item', backref='seller', lazy=True, foreign_keys=[sold_item_id])
    bought_item = db.relationship('Item', backref='buyer', lazy=True, foreign_keys=[bought_item_id])
    role = db.Column(db.Enum(Role))

    def __repr__(self):
        return '<User %r>' % self.username

    @hybrid_property
    def password_hash(self):
        return self._password_hash;

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)


class Item(db.Model, ObjectABC):
    id = db.Column(db.Integer, primary_key=True)
    _category = db.relationship('Category', backref='item', lazy=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    _subcategory = db.relationship('Subcategory', backref='item', lazy=True)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'), nullable=True)
    _image = db.relationship('Image', backref='item', lazy=True)

    def __repr__(self):
        return '<Item %r>' % self.name

    @hybrid_property
    def category(self):
        return self._category

    @category.setter
    def category(self, category_name):
        category = Category.query.filter_by(name=category_name).first_or_404()
        self.category_id = category.id

    @hybrid_property
    def subcategory(self):
        return self._subcategory

    @subcategory.setter
    def subcategory(self, subcategory_name):
        subcategory = Subcategory.query.filter_by(name=subcategory_name).first_or_404()
        self.subcategory_id = subcategory.id

    @hybrid_property
    def image(self):
        return self._image

    @image.setter
    def image(self, image_name):
        image = Image.query.filter_by(name=image_name).first_or_404()
        image.item_id = self.id

    def update(self, parameters):
        super().update(parameters)
        if parameters.get('category'):
            self.category = parameters['category']
        if parameters.get('subcategory'):
            self.subcategory = parameters['subcategory']
        if parameters.get('image'):
            self.image = parameters['image']


class Category(db.Model, ObjectABC):
    id = db.Column(db.Integer, primary_key=True, unique=True)

    def update(self, parameters):
        super().update(parameters)

    def __repr__(self):
        return '<Category %r>' % self.name


class Subcategory(db.Model, ObjectABC):
    id = db.Column(db.Integer, primary_key=True)
    _category = db.relationship('Category', backref='subcategory', lazy=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    @hybrid_property
    def category(self):
        return self._category

    @category.setter
    def category(self, category_name):
        category = Category.query.filter_by(name=category_name).first_or_404()
        self.category_id = category.id

    def update(self, parameters):
        super().update(parameters)
        if parameters.get('category'):
            self.category = parameters['category']

    def __repr__(self):
        return '<Subcategory %r>' % self.name


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    img_data = db.Column(db.LargeBinary, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)

    def __repr__(self):
        return '<Image %r>' % self.name
