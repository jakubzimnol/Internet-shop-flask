from sqlalchemy import exc

from init_app import db


class Repository:
    @staticmethod
    def add_to_database(item):
        try:
            db.session.add(item)
            db.session.commit()
            return True
        except exc.IntegrityError:
            db.session.rollback()
            return False

    @classmethod
    def create_and_add(cls, model, dictionary):
        dict_without_none = {k: v for k, v in dictionary.items() if v is not None}
        new_object = model(**dict_without_none)
        if cls.add_to_database(new_object):
            return new_object
        return False

