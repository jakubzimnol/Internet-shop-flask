from sqlalchemy import exc

from app.models import Image
from init_app import db


class Repository():
    def add_to_database(self, item):
        try:
            db.session.add(item)
            db.session.commit()
            return True
        except exc.IntegrityError:
            db.session.rollback()
            return False

    def upload_image(self, image_dict):
        new_image = Image(name=image_dict['name'], img_data=image_dict['img_data'], item_id=image_dict['item_id'])
        db.session.add(new_image)
        db.session.commit()

