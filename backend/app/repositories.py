from flask_jwt_extended import get_jwt_identity
from sqlalchemy import exc, exists

from app.exceptions import IntegrityException
from app.models import User, Role
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

    @staticmethod
    def get_logged_user():
        current_user_name = get_jwt_identity()
        return User.query.filter_by(username=current_user_name).first()

    @classmethod
    def check_role(cls, role_names):
        user = cls.get_logged_user()
        return user and user.roles in role_names

    @classmethod
    def is_admin_role(cls):
        user = cls.get_logged_user()
        return user and user.roles is Role.ADMIN

    # @staticmethod
    # def change_name_to_object_list(model, objects, obj_name):
    #     for obj in objects:
    #         name = obj.pop('name')
    #         obj[obj_name] = model.query.filter_by(name=name).first_or_404()
    #     return objects

    @classmethod
    def create_and_add_objects_list(cls, model, objects):
        return [cls.create_and_add(model, obj_dict) for obj_dict in objects]
