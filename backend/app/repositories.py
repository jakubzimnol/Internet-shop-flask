from sqlalchemy import exc

from app.models import Image
from init_app import db


class Repository():
    @staticmethod
    def add_to_database(item):
        try:
            db.session.add(item)
            db.session.commit()
            return True
        except exc.IntegrityError:
            db.session.rollback()
            return False

    @staticmethod
    def upload_image(image_dict):
        new_image = Image(name=image_dict['name'], img_data=image_dict['img_data'], item_id=image_dict['item_id'])
        db.session.add(new_image)
        db.session.commit()


