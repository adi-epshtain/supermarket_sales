from sqlalchemy.exc import IntegrityError
from enum import Enum
import random
import logging as log

from supermarket_sales.conf import db
from supermarket_sales.dbmodels.Item.model import Item


class SaleType(Enum):
    SALE1 = 1
    SALE2 = 2


class SuperSale(db.Model):
    """
    Sale class (abstract class)
    """
    __tablename__ = 'Sale'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    amount = db.Column(db.Integer, nullable=True, default=None)
    discount = db.Column(db.Float, nullable=True, default=None)
    sale_type = db.Column(db.Enum(SaleType))
    item_id = db.Column(db.String(80), nullable=False)  # one to one relationship
    buy_amount = db.Column(db.Integer, nullable=True, default=None)

    def __init__(self, item_id: str, amount: int, discount: float, sale_type: SaleType, buy_amount=None):
        self.id = random.choice(range(1, 100000001))
        self.amount = amount
        self.discount = discount
        self.sale_type = sale_type
        self.item_id = item_id
        self.buy_amount = buy_amount  # relevant only to sale type 1 (buy x get y -> buy_amount=x, amount=x+y)

    def __repr__(self):
        return f"buy x: {self.amount} items get discount: {self.discount}"

    @staticmethod
    def delete_all():
        """
        delete all sales records on DB
        """
        try:
            log.warning("delete all sales")

            db.session.query(SuperSale).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            log.error(f"Failed to delete all rows in Sale table, error: {e}")

    @staticmethod
    def add_sale1(item_id: str, buy_items: int, gift_items: int):
        """
        add sale type 1 buy x get y to item with item_id
        """
        item_obj = Item.get_item_by_id(item_id)
        if item_obj:
            amount = buy_items + gift_items
            discount = amount * item_obj.price - buy_items * item_obj.price
            sale = SuperSale(item_id, amount, discount, sale_type=SaleType.SALE1, buy_amount=buy_items)

            try:
                db.session.add(sale)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                log.error("Trying to add sale type 1 object with exist primary key. Aborting")
        else:
            log.error(f"sorry item id: {item_id} is not exist, failed to add sale")

    @staticmethod
    def add_sale2(item_id: str, buy_items: int, sale_price: float):
        """
        add sale type 2 buy x on special price to item with item_id
        """
        item_obj = Item.get_item_by_id(item_id)
        if item_obj:
            discount = buy_items * item_obj.price - sale_price
            sale = SuperSale(item_id, amount=buy_items, discount=discount, sale_type=SaleType.SALE2)
            try:
                db.session.add(sale)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                log.error("Trying to add sale type 2 object with exist primary key. Aborting")
        else:
            log.error(f"sorry item id: {item_id} is not exist, failed to add sale")

    @staticmethod
    def get_sale_details_by_item_id(item_id) -> (int, int, int):
        """
        return sale details: amount, discount or 0, 0, 0 case there is no sale1
        """
        sales_obj = db.session.query(SuperSale).filter(SuperSale.item_id == item_id).one_or_none()

        if not sales_obj:
            log.error(f"item with id: {item_id} is not found")
            return 0, 0, 0

        return sales_obj.amount, sales_obj.discount, sales_obj.buy_amount

    @staticmethod
    def get_all_sales():
        return db.session.query(SuperSale).all()
