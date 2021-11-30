from collections import Counter
import logging as log

from supermarket_sales.dbmodels.Sale.model import SuperSale
from supermarket_sales.dbmodels.Item.model import Item
from supermarket_sales.conf import db, app


def get_total_payment(basket: dict) -> float:
    total_payment = 0

    for item_id, item_amount in basket.items():
        lose_money = 0
        item_obj = Item.get_item_by_id(item_id)
        if item_obj:
            regular_payment = item_obj.price * item_amount

            sale_amount, sale_discount, buy_amount = SuperSale.get_sale_details_by_item_id(item_id)

            num_sale = item_amount // sale_amount  # how many times sale is exist on basket, case no sale -> 0 discount

            x = item_amount % sale_amount
            if buy_amount and x in range(buy_amount + 1, sale_amount + 1):
                num_sale += 1
                lose_money = (sale_amount - x) * item_obj.price
                log.warning(f"sale. buy {buy_amount} get {sale_amount - buy_amount} you get only {x}."
                            f" lose money: {lose_money}")

            item_discount = num_sale * sale_discount

            log.warning(f"id: {item_id}, amount: {item_amount}, regular_payment: {regular_payment} "
                        f"item discount: {item_discount}")

            payment = regular_payment - item_discount + lose_money
            total_payment += payment

    return total_payment


if __name__ == '__main__':

    db.create_all()

    Item.delete_all()
    SuperSale.delete_all()

    apple = Item(item_id="1111", name="Apple", price=2.00).add_item()
    SuperSale.add_sale1(item_id="1111", buy_items=3, gift_items=4)

    peach = Item(item_id="2222", name="peach", price=3.00).add_item()
    SuperSale.add_sale1(item_id="2222", buy_items=4, gift_items=5)

    beer = Item(item_id="3333", name="beer", price=10.00).add_item()
    SuperSale.add_sale2(item_id="3333", buy_items=6, sale_price=50.00)

    cola = Item(item_id="4444", name="cola", price=7.00).add_item()
    SuperSale.add_sale2(item_id="4444", buy_items=3, sale_price=15.00)

    banana = Item(item_id="5555", name="banana", price=4.20).add_item()

    shopping_basket = Counter({'2222': 15, '4444': 7, '3333': 3, '1111': 5})
    total_price = get_total_payment(shopping_basket)

    log.warning(f"please pay: {total_price}")

