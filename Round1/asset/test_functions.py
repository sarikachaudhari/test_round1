import datetime, csv, json
from django.contrib.auth.models import User, Group
from asset.models import *
from supplier.models import *
from department.models import *

from django.db import transaction, IntegrityError
from django.db.models import Q, Max
from asset.helper_functions import *

# Department Ids
STORE_ID = 2
KITCHEN_ID = 3

# Stock item Ids
SUGAR = 1
TEA = 2
CHAPATI = 3
AALOO_PARATHA_ID = 4
PITH = 5

def test_transfer_stock_between_departments():
    stock_items = [
        {
            "stock_item_id": 2,
            "quantity": 2
        },
        {
            "stock_item_id": 5555,
            "quantity": 1
        }
    ]

    source_dept = STORE_ID
    dest_dept = KITCHEN_ID

    transfer_stock_between_departments(source_dept, dest_dept, stock_items)

def test_consume_item_from_department():

    dept_id = KITCHEN_ID

    stock_items_to_consume = [
        {
            "stock_item_id": TEA,
            "quantity": 2
        }
    ]
    consume_item_from_department(stock_items_to_consume, dept_id)

def test_add_item_to_department():

    dept_id = KITCHEN_ID

    stock_items_to_add = [
        {
            "stock_item_id": TEA,
            "quantity": 5
        }
    ]
    add_item_to_department(stock_items_to_add, dept_id)

def test_overwrite_department_stock():

    dept_id = KITCHEN_ID

    stock_items_in_department = [
        {
            "stock_item_id": TEA,
            "quantity": 100
        }
    ]
    overwrite_department_stock(stock_items_in_department, dept_id)

def test_create_recipe():
    produced_stock_item_id = 4
    produced_item_quantity = 30
    ingredients_list = [
        {
            "stock_item_id": 5,
            "quantity": 1
        },
        {
            "stock_item_id": 1,
            "quantity": 0.5
        }
    ]
    create_recipe(produced_stock_item_id, produced_item_quantity, ingredients_list)

def test_produce_items_with_recipe():
    department_id = KITCHEN_ID

    produced_stock_items = [
        {
            "produced_stock_item_id": AALOO_PARATHA_ID,
            "produced_quantity": 0
        }
    ]

    produce_items_with_recipe(produced_stock_items, department_id)

def test_produce_items_with_recipe_and_transfer():
    department_id = KITCHEN_ID

    produced_stock_items = [
        {
            "produced_stock_item_id": CHAPATI,
            "produced_quantity": 15
        }
    ]

    produce_items_with_recipe_and_transfer(produced_stock_items, department_id)

def test_create_purchase_order_draft():
    supplier_id = 1
    dest_department_id = 3
    item_list = [
        {
            "stock_item_id": 1,
            "requested_quantity": -12,
            "requested_unit_price": 10
        }
    ]
    create_purchase_order_draft(item_list, supplier_id, dest_department_id)

def test_purchase_order_honoured():
    purchase_order_id = 2
    item_list = [
        {
            "stock_item_id": 1,
            "received_quantity": 45,
            "received_unit_price": 9
        }
    ]
    purchase_order_honoured(purchase_order_id, item_list)

def test_create_stock_transfer_request_draft():
    source_department_id = 1
    dest_department_id = 2
    item_list = [
        {
            "stock_item_id": 1,
            "requested_quantity": 0
        }
    ]
    create_stock_transfer_request_draft(source_department_id, dest_department_id, item_list)

def test_stock_transfer_request_honoured():
    stock_transfer_request_id = 2
    item_list = [
        {
            "stock_item_id": 1,
            "received_quantity": 45
        }
    ]
    stock_transfer_request_honoured(stock_transfer_request_id, item_list)

# ----------------------------------------------------------------------------------------------

def test_get_stock_report():

    get_stock_report()


def test_create_system_verification_checkpoint():

    create_system_verification_checkpoint()


def test_create_manual_verification_checkpoint():
    KITCHEN_ID = 3
    STORE_ID = 2
    AALOO_PARATHA_ID = 4
    SUGAR_ID = 1
    manaul_verification_data = [{
                                "department_id": KITCHEN_ID,
                                "stock_item_id": AALOO_PARATHA_ID,
                                "quantity": 5,
                               },
                               {
                                "department_id": STORE_ID,
                                "stock_item_id": SUGAR_ID,
                                "quantity": 200,
                               }]

    create_manual_verification_checkpoint(manaul_verification_data)


def test_create_sale_order_draft():
    item_dict ={
                "order_code": "DCF1254",
                "order_type": 1,
                "placed_date": 1497265250000,
                "item_list": [{"stock_item_id": 3, "quantity": -22}, {"stock_item_id": 4, "quantity": 4}]
               }

    create_sale_order_draft(item_dict["item_list"], item_dict["order_code"], item_dict["order_type"])

def test_sale_order_honoured():
    sale_order_id = 15

    sale_order_honoured(sale_order_id)


def test_create_department_stock():
    stock_item_id = 1
    department_id = 1
    quantity = -0

    create_department_stock(stock_item_id, department_id, quantity)
