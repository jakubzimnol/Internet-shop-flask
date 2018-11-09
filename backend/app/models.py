import enum
from abc import ABC, abstractmethod

from sqlalchemy import exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

from app.exceptions import IntegrityException
from init_app import db


class AbstractUpdater(ABC):
    name = None

    @abstractmethod
    def update(self, parameters):
        if parameters.get('name'):
            self.name = parameters['name']


Base = declarative_base()


class PayuStatus(enum.Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"


class Status(enum.Enum):
    NEW = "New"
    PAID = "Paid"
    SEND = "Send"
    FINISHED = "Finished"
    CANCELED = "Canceled"


class Role(enum.Enum):
    ADMIN = "Admin"
    SELLER = "Seller"
    BUYER = "Buyer"

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    _password_hash = db.Column(db.String(128))
    sold_item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    bought_item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    sold_item = db.relationship('Item', backref='seller', lazy=True, foreign_keys=[sold_item_id])
    bought_item = db.relationship('Item', backref='buyer', lazy=True, foreign_keys=[bought_item_id])
    _roles = db.Column(db.Enum(Role))

    def __repr__(self):
        return '<User %r>' % self.username

    @hybrid_property
    def roles(self):
        return self._roles

    @roles.setter
    def roles(self, role):
        try:
            self._roles = Role(role)
        except ValueError:
            raise IntegrityException()

    @hybrid_property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)


@AbstractUpdater.register
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    _category = db.relationship('Category', backref='item', lazy=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    _subcategory = db.relationship('Subcategory', backref='item', lazy=True)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'), nullable=True)
    _image = db.relationship('Image', backref='item', lazy=True)
    price = db.Column(db.Integer, nullable=False, default=0)
    amount = db.Column(db.Integer, nullable=False, default=1)

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

    @hybrid_property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, user_name):
        user = User.query.filter_by(name=user_name).first_or_404()
        self.owner_id = user.id

    def update(self, parameters):
        if parameters.get('name'):
            self.name = parameters['name']
        if parameters.get('category'):
            self.category = parameters['category']
        if parameters.get('subcategory'):
            self.subcategory = parameters['subcategory']
        if parameters.get('image'):
            self.image = parameters['image']


class OrderedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _item = db.relationship('Item', backref='ordered_item', lazy=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

    @hybrid_property
    def item(self):
        return self._item

    @item.setter
    def item(self, name):
        item = Item.query.filter_by(name=name).first_or_404()
        self.item_id = item.id


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    ordered_items = db.relationship('OrderedItem', backref=db.backref('order', lazy=True))
    payu_order_id = db.Column(db.String(120), nullable=True)
    buyer = db.relationship('User', backref='order', lazy=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    _payment_status = db.Column(db.Enum(PayuStatus), default=PayuStatus.NEW)
    _status = db.Column(db.Enum(Status), default=Status.NEW)

    @hybrid_property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        try:
            self._status = getattr(Status, status)
        except AttributeError:
            raise IntegrityException()

    @hybrid_property
    def payment_status(self):
        return self._payment_status

    @payment_status.setter
    def payment_status(self, status_name):
        try:
            self._payment_status = PayuStatus(status_name)
        except ValueError:
            raise IntegrityException()


@AbstractUpdater.register
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def update(self, parameters):
        if parameters.get('name'):
            self.name = parameters['name']

    def __repr__(self):
        return '<Category %r>' % self.name


@AbstractUpdater.register
class Subcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
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
        if parameters.get('name'):
            self.name = parameters['name']
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


class RevokedTokenModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jwi = db.Column(db.String(120))

    @classmethod
    def is_blacklisted(cls, jwi):
        return db.session.query(exists().where(cls.jwi == jwi)).scalar()
