import datetime, csv, json
from asset.models import *
from Round1.models import *
from helper_functions import convert_epoch_to_date
from .helper_functions import validate_quantity

#-------------------------------------pc------------------------------------------------#

def validate_stock_item(params):
    kwargs = {}

    params = params.get("data")
    code = params.get("code")
    name = params.get("name")
    regional_name = params.get("regional_name")
    brand = params.get("brand")
    sale_price = params.get("sale_price")
    usage_type = params.get("usage_type")
    nature = params.get("nature")
    quantity_unit = params.get("quantity_unit")
    tax_rate = params.get("tax_rate")
    description = params.get("description")
    shelf_life = params.get("shelf_life")
    notes = params.get("notes")
    is_active = params.get("is_active")

    print('params: ', params)
    if not sale_price:
        sale_price = 0.0

    if (not code) or (not name) or (not regional_name):
        return kwargs, "Invalid data", False

    if StockItem.objects.filter(code=code).exists():
        return kwargs, "Stock item code is already exists", False

    if tax_rate:
        tax_rate, created = TaxRate.objects.get_or_create(rate=tax_rate)
    else:
        tax_rate, created = TaxRate.objects.get_or_create(rate=0.0)

    print(tax_rate.rate)

    kwargs = {
                "code": code,
                "name": name,
                "regional_name": regional_name,
                "brand": brand,
                "sale_price": sale_price,
                "usage_type": usage_type,
                "nature": nature,
                "quantity_unit": quantity_unit,
                "tax_rate": tax_rate,
                "description": description,
                "shelf_life": shelf_life,
                "notes": notes,
                "is_active": is_active
            }
    print('kwargs: ', kwargs)
    return kwargs, "Stock item saved", True


def validate_stock_transfer_request(params):

    source_dept_id = params.get("source_dept_id")
    dest_dept_id = params.get("dest_dept_id")
    stock_item_list = params.get("stock_item_list")

    if not source_dept_id:
        return False, None, "Source dept not found"

    if not dest_dept_id:
        return False, None, "Dest dept not found"

    if source_dept_id == dest_dept_id:
        return False, None, "Source and destination departments are same"

    if not stock_item_list and not isinstance(stock_item_list, list):
        return False, None, "Stock items not found"

    if len(stock_item_list) <= 0:
        return False, None, "No stock items provided"

    item_ids = [x['stock_item_id'] for x in stock_item_list if 'stock_item_id' in x]
    if len(item_ids) != len(set(item_ids)):
        return False, None, "Requested items cant be repeated"

    for stock_item in stock_item_list:
        if not 'stock_item_id' in stock_item:
            return False, None, "Stock item id not found"
        if not 'requested_quantity' in stock_item:
            return False, None, "Requested quantity not found"
        if float(stock_item['requested_quantity']) <= 0.0:
            return False, None, "Requested quantity should be greater than zero"

    data = {
        "source_dept_id" : source_dept_id,
        "dest_dept_id" : dest_dept_id,
        "stock_item_list" : stock_item_list
    }

    return True, data, "Success"


def validate_purchase_order(params):

    supplier_id = params.get("supplier_id")
    dest_department_id = params.get("dest_department_id")
    item_list = params.get("item_list")

    if not supplier_id:
        return False, None, "Supplier not found"

    if not dest_department_id:
        return False, None, "Dest dept not found"

    if not item_list and not isinstance(item_list, list):
        return False, None, "Stock items not found"

    if len(item_list) <= 0:
        return False, None, "No stock items provided"

    item_ids = [x['stock_item_id'] for x in item_list if 'stock_item_id' in x]
    if len(item_ids) != len(set(item_ids)):
        return False, None, "Requested items cant be repeated"

    for stock_item in item_list:
        if not 'stock_item_id' in stock_item:
            return False, None, "Stock item id not found"
        if not 'requested_quantity' in stock_item:
            return False, None, "Requested quantity not found"
        if float(stock_item['requested_quantity']) <= 0.0:
            return False, None, "Requested quantity should be greater than zero"

    data = {
        "supplier_id" : supplier_id,
        "dest_department_id" : dest_department_id,
        "item_list" : item_list
    }

    return True, data, "Success"


def validate_mark_purchase_order_completed(params):

    purchase_order_id = params.get("purchase_order_id")
    item_list = params.get("item_list")

    if not purchase_order_id:
        return False, None, "Purchase order id not found"

    try:
        purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
    except Exception as e:
        return False, None, "Invalid purchase order"

    if purchase_order.status == PURCHASE_ORDER_STATUS[1][0]: # Canceled
        return False, None, "Purchase order is Canceled"

    if purchase_order.status == PURCHASE_ORDER_STATUS[3][0]: # Complete
        return False, None, "Purchase order is already completed"

    if not item_list and not isinstance(item_list, list):
        return False, None, "Stock items not found"

    if len(item_list) <= 0:
        return False, None, "No stock items provided"

    item_ids = [x['stock_item_id'] for x in item_list if 'stock_item_id' in x]
    if len(item_ids) != len(set(item_ids)):
        return False, None, "Received items cant be repeated"

    order_item_ids = [x.item.id for x in purchase_order.get_purchase_order_items.all()]

    for stock_item in item_list:
        if not 'stock_item_id' in stock_item:
            return False, None, "Stock item id not found"
        if not stock_item['stock_item_id'] in order_item_ids:
            return False, None, "Stock item not found in purchase order"
        if not 'received_quantity' in stock_item:
            return False, None, "Received quantity not found"
        if float(stock_item['received_quantity']) <= 0.0:
            return False, None, "Received quantity should be greater than zero"
        if "received_unit_price" in stock_item:
            print(type(stock_item["received_unit_price"]))
            if isinstance(stock_item["received_unit_price"], str) or stock_item["received_unit_price"] is None:
                pass
            elif not isinstance(stock_item["received_unit_price"], int) and not isinstance(stock_item["received_unit_price"], float):
                return False, None, "invalid received unit price"

    data = {
        "purchase_order_id" : purchase_order_id,
        "item_list" : item_list
    }

    return True, data, "Success"


def validate_sale_order(params):
    order_code = params.get("order_code")
    placed_date = params.get("placed_date")
    order_type = params.get("order_type")
    item_list = params.get("item_list")

    if not placed_date:
        return False, None, "Enter sale order date"

    if order_type not in [i[0] for i in SALE_ORDER_STATUS]:
        return False, None, "Invalid order type"

    if not item_list and not isinstance(item_list, list):
        return False, None, "Stock items not found"

    if len(item_list) <= 0:
        return False, None, "No stock items provided"

    ## Return, if item list has duplicate entries of item
    item_ids = [x['stock_item_id'] for x in item_list if 'stock_item_id' in x]
    if len(item_ids) != len(set(item_ids)):
        return False, None, "Input items cant be repeated"

    for stock_item in item_list:
        if not 'stock_item_id' in stock_item:
            return False, None, "Stock item id not found"
        if not 'quantity' in stock_item:
            return False, None, "Quantity not found"
        if float(stock_item['quantity']) <= 0.0:
            return False, None, "Quantity should be greater than zero"

    data = {
        "order_code": order_code if order_code else None,
        "placed_date": convert_epoch_to_date(placed_date),
        "order_type": order_type,
        "item_list": item_list,
    }

    return True, data, "Order Placed Successfully"


def validate_recipe(params):

    produced_stock_item_id = params.get("produced_stock_item_id")
    produced_item_quantity = params.get("produced_item_quantity")
    ingredients_list = params.get("ingredients_list")

    if not produced_stock_item_id:
        return False, None, "Produced stock item id not found"

    if Recipe.objects.filter(produced_item=produced_stock_item_id).exists():
        return False, None, "Recipe already exists"

    if not StockItem.objects.filter(id=produced_stock_item_id, usage_type=USAGE_TYPE[1][0]).exists(): # Finished Product
        return False, None, "Produced item must be finished product"

    if not produced_item_quantity:
        return False, None, "Produced item quantity not found"

    if produced_item_quantity <= 0.0:
        return False, None, "Invalid produced item quantity. should be greater than zero"

    if not ingredients_list and not isinstance(ingredients_list, list):
        return False, None, "Invalid ingredients."

    if len(ingredients_list) <= 0:
        return False, None, "No ingrediants provided"

    ingredients_ids = [x['stock_item_id'] for x in ingredients_list if 'stock_item_id' in x]
    if len(ingredients_ids) != len(set(ingredients_ids)):
        return False, None, "Ingredients cant be repeated"

    new_ingredients_list = []
    for ingredient in ingredients_list:
        if not 'stock_item_id' in ingredient:
            return False, None, "Stock item id not found"
        if produced_stock_item_id == ingredient['stock_item_id']:
            return False, None, "Item to produce cant be in ingredients"
        if StockItem.objects.filter(id=ingredient['stock_item_id'], usage_type=USAGE_TYPE[2][0]).exists(): # Appliance
            return False, None, "Ingredient cant be appliance"
        if not 'quantity' in ingredient:
            return False, None, "quantity not found in ingredient"
        if float(ingredient['quantity']) <= 0.0:
            return False, None, "ingredient quantity should be greater than zero"
        new_ingredients_list.append({
            "stock_item_id" : ingredient['stock_item_id'],
            "quantity": ingredient['quantity']
        })

    new_data = {
        "produced_stock_item_id" : produced_stock_item_id,
        "produced_item_quantity" : produced_item_quantity,
        "ingredients_list" : new_ingredients_list
    }

    return True, new_data, "Success"


def validate_produce_finished_item(params):

    department_id = params.get("department_id")
    produced_stock_items = params.get("produced_stock_items")

    # if not department_id:
    #     return False, None, "Department id not found"

    if not produced_stock_items and not isinstance(produced_stock_items, list):
        return False, None, "Invalid ingredients."

    if len(produced_stock_items) <= 0:
        return False, None, "No ingrediants provided"

    produced_ids = [x['produced_stock_item_id'] for x in produced_stock_items if 'produced_stock_item_id' in x]
    if len(produced_ids) != len(set(produced_ids)):
        return False, None, "Produced items cant be repeated"

    for stock_item in produced_stock_items:
        if not 'produced_stock_item_id' in stock_item:
            return False, None, "Produced stock item id not found"
        if StockItem.objects.filter(id=stock_item['produced_stock_item_id'], usage_type=USAGE_TYPE[2][0]).exists(): # Appliance
            return False, None, "Produced item cant be appliance"

        recipes = Recipe.objects.filter(produced_item=stock_item['produced_stock_item_id'])
        if not recipes.exists():
            return False, None, "Produced item recipe not found"

        try:
            json.loads(recipes[0].ingredients_json)
        except:
            return False, None, "Invalid recipe contents"

        if not 'produced_quantity' in stock_item:
            return False, None, "Produced quantity not found in produced item"
        if float(stock_item['produced_quantity']) <= 0.0:
            return False, None, "Produced quantity should be greater than zero"

    new_data = {
        "department_id" : department_id if department_id else None,
        "produced_stock_items" : produced_stock_items
    }

    return True, new_data, "Success"

#--------------------------------------aw----------------------------------------------#


def validate_manual_stock_verification_checkpoint(data):
    if not isinstance(data, list):
        return False, None, 'Invalid input'

    if len(data) < 1:
        return False, None, 'Add item for manual stock verification'

    for item in data:
        if not 'stock_item_id' in item:
            return False, None, "Stock item id not found"
        if not 'department_id' in item:
            return False, None, "Department id not found"
        if not 'quantity' in item:
            return False, None, "Quantity not found in item"
        if float(item['quantity']) < 0.0:
            return False, None, "Stock item quantity should not be negative"

    return True, data, 'Success'
