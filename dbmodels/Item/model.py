from supermarket_sales.conf import db
from sqlalchemy.exc import IntegrityError

import logging as log


class Item(db.Model):
    """
    Item class
    """
    id = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float(80), nullable=False)

    def __init__(self, item_id: str, name: str, price: float):
        self.id = item_id
        self.name = name
        self.price = price

    def add_item(self):
        """
        add new item to DB
        :return: item
        """
        log.warning("add item: {}".format(self.id))
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            log.error(f"Trying to add new Item object with exist primary key. Aborting {error}")
            return None
        return self

    @staticmethod
    def delete_all():
        """
        delete all items records on DB
        """
        try:
            log.warning("delete all items")

            db.session.query(Item).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            log.error(f"Failed to delete all rows in Item table, error:{e}")

    @staticmethod
    def get_item_by_id(item_id: str):
        """
        get item by id or None if not exist
        """
        item = db.session.query(Item).filter(Item.id == item_id).one_or_none()

        if not item:
            log.error(f"item with id: {item_id} is not found")

        return item

    @staticmethod
    def get_all_items():
        return db.session.query(Item).all()
