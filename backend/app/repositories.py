from sqlalchemy import exc, exists

from app.exceptions import IntegrityException
from init_app import db


class Repository:
    @staticmethod
    def add_to_database(item):
        try:
            db.session.add(item)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            raise IntegrityException()

    @classmethod
    def create_and_add(cls, model, dictionary):
        dict_without_none = {k: v for k, v in dictionary.items() if v is not None}
        new_object = model(**dict_without_none)
        cls.add_to_database(new_object)
        return new_object

    @staticmethod
    def check_unique_name(value, model):
        return db.session.query(exists().where(model.name == value)).scalar()
