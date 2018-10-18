import enum

from app import db


class Role(enum.Enum):
    ADMIN = "Admin"
    SELLER = "Seller"
    BUYER = "Buyer"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    bought = db.relationship('Item', backref='buyer', lazy=True)
    sold = db.relationship('Item', backref='seller', lazy=True)
    role = db.Column(db.Enum(Role))

    def __repr__(self):
        return '<User %r>' % self.username


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    category = db.relationship('Category', backref='item', lazy=True, nullable=True)
    subcategory = db.relationship('Subcategory', backref='item', lazy=True, nullable=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyer.id'), nullable=True)
    image = db.relationship('Image', backref='item', lazy=True, nullable=True)

    def __repr__(self):
        return '<Item %r>' % self.name


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)

    def __repr__(self):
        return '<Category %r>' % self.name


class Subcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    category = db.relationship('Subcategory', backref='item', lazy=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)

    def __repr__(self):
        return '<Subcategory %r>' % self.name


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    img_data = db.Column(db.LargeBinary, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)

    def __repr__(self):
        return '<Image %r>' % self.name


def add_image(image_dict):
    new_image = Image(name=image_dict['name'], img_data=image_dict['img_data'], item_id=image_dict['item_id'])
    db.session.add(new_image)
    db.session.commit()
