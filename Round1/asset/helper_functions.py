import datetime, csv, json
from django.contrib.auth.models import User, Group
from asset.models import *
from supplier.models import *
from department.models import *
from Round1.models import *

from django.db import transaction, IntegrityError
from django.db.models import Q, Max

from Round1.helper_functions import convert_epoch_to_date
from Round1.settings import \
    DEBUG


def validate_quantity(quantity, negative_allowed, zero_allowed, positive_allowed=True):
    print('Validate quantity function')
    try:
        quantity = float(quantity)
        print('quantity: ', quantity)
    except Exception as e:
        print(e)
        return False

    if quantity < 0.0:
        print('Checking negative validation')
        if negative_allowed:
            return True
        else:
            return False

    elif quantity == 0.0:
        print('Checking Zero validation')
        if zero_allowed:
            return True
        else:
            return False

    elif quantity > 0.0:
        print('Checking Positive validation')
        if positive_allowed:
            return True
        else:
            return False

    print('Validate quantity function end')


def transfer_stock_between_departments(source_dept_id, dest_dept_id, stock_items):
    '''
        Quantity of stock items cannot be negative or zero.
    '''
    print('============================ transfer_stock_between_departments ============================')
    try:
        with transaction.atomic():
            for stock_item in stock_items:
                res = validate_quantity(stock_item['quantity'], negative_allowed=False, zero_allowed=False)
                if not res:
                    raise Exception('Stock quantity should be positive')

                print('')
                source_department_stock = get_or_create_new_department_stock(stock_item['stock_item_id'], source_dept_id)
                if not source_department_stock:
                    raise Exception('Failed to create source department stock entry')

                dest_department_stock = get_or_create_new_department_stock(stock_item['stock_item_id'], dest_dept_id)
                if not dest_department_stock:
                    raise Exception('Failed to create dest department stock entry')

                source_department_stock.quantity -= stock_item['quantity']
                dest_department_stock.quantity += stock_item['quantity']

                source_department_stock.save()
                dest_department_stock.save()
                print('success: transfered ', source_department_stock, 'to', dest_department_stock, 'quantity:', stock_item['quantity'])
                print('------------------------------')
            # End of for loop
            print ('Success transfer_stock_between_departments')
            return True
    except Exception as e:
        print ('Error in transfer_stock_between_departments: ', e)
        print ('Rolling back stock transfer trancation')
        return False


def create_department_stock(stock_item_id, department_id, quantity=0):
    '''
        Quantity of stock items cannot be negative.
    '''
    try:
        with transaction.atomic():
            res = validate_quantity(quantity, negative_allowed=False, zero_allowed=True)
            if not res:
                raise Exception('Stock quantity cannot be negative')

            stock_item = StockItem.objects.get(id=stock_item_id)
            department = Department.objects.get(id=department_id)

            department_stock = DepartmentStock()
            department_stock.stock_item = stock_item
            department_stock.department = department
            department_stock.quantity = quantity
            department_stock.quantity_unit = stock_item.quantity_unit
            department_stock.save()
            return department_stock
    except Exception as e:
        print(e)
        return None

def produce_items_with_recipe_and_transfer(produced_stock_items, department_id=None):
    if not department_id:
        try:
            print('produce_items_with_recipe_and_transfer, getting default_production_department from config table')
            department_id = SystemClientConfig.objects.get(key='default_production_department').value
        except Exception as e:
            print('Error in produce_items_with_recipe_and_transfer, default_production_department not found: ', e)
            return None

    auto_transfer_produced_items = False
    default_sale_department_id = None
    try:
        bool_string = SystemClientConfig.objects.get(key='auto_transfer_produced_items').value
        if bool_string.upper() == 'TRUE':
            try:
                default_sale_department_id = SystemClientConfig.objects.get(key='default_sale_department').value
            except Exception as e:
                print('Error in produce_items_with_recipe_and_transfer, auto_transfer_produced_items is true but default_sale_department not found: ', e)
                return None
            auto_transfer_produced_items = True
    except Exception as e:
        print('Error in produce_items_with_recipe_and_transfer, auto_transfer_produced_items not found: ', e)

    print('produce_items_with_recipe_and_transfer, auto_transfer_produced_items: ', auto_transfer_produced_items)
    # ------------------------------------------------------------

    try:
        with transaction.atomic():
            res = produce_items_with_recipe(produced_stock_items, department_id)
            if not res:
                raise Exception('Failed to produce_items_with_recipe')

            if auto_transfer_produced_items:
                stock_items_to_transfer = []
                for produced_stock_item in produced_stock_items:
                    stock_items_to_transfer.append({
                        "stock_item_id": produced_stock_item['produced_stock_item_id'],
                        "quantity": produced_stock_item['produced_quantity']
                    })
                # End of for loop

                source_dept = department_id
                dest_dept = default_sale_department_id
                print('produce_items_with_recipe_and_transfer, auto transfering produced items')
                res = transfer_stock_between_departments(source_dept, dest_dept, stock_items_to_transfer)
                if not res:
                    raise Exception('Failed to transfer stock between department')
            # End of if statement for auto_transfer_produced_items
            return True
    except Exception as e:
        print('Error in produce_items_with_recipe_and_transfer: ', e)
        return False

def produce_items_with_recipe(produced_stock_items, department_id):
    '''
        Quantity of produced stock items cannot be negative or zero.
    '''

    try:
        with transaction.atomic():

            for produced_stock_item in produced_stock_items:
                produced_stock_item_id = produced_stock_item['produced_stock_item_id']
                produced_quantity = produced_stock_item['produced_quantity']

                res = validate_quantity(produced_quantity, negative_allowed=False, zero_allowed=False)
                if not res:
                    raise Exception('Stock quantity should be positive')

                # Increase produced item quantity
                produced_department_stock = get_or_create_new_department_stock(produced_stock_item_id, department_id)
                if not produced_department_stock:
                    raise Exception('Failed to create department stock entry')

                produced_department_stock.quantity += produced_quantity
                produced_department_stock.save()

                # Get recipe and ingredients
                recipe = Recipe.objects.get(produced_item=produced_stock_item_id)
                ingredients = json.loads(recipe.ingredients_json)

                # Decrease ingredient item quantity
                for ingredient in ingredients:
                    ingredient_department_stock = get_or_create_new_department_stock(ingredient['stock_item_id'], department_id)
                    if not ingredient_department_stock:
                        raise Exception('Failed to create department stock entry')

                    consumed_qty = (float(produced_quantity)/float(recipe.produced_item_quantity)) * ingredient['quantity']

                    ingredient_department_stock.quantity -= consumed_qty
                    ingredient_department_stock.save()
                    print('success produce_item_with_recipe: ', ingredient_department_stock)
            # End of for loop
            return True
    except Exception as e:
        print('Error in produce_item_with_recipe: ', e)
        return False


def overwrite_department_stock(stock_items_in_department, department_id):
    try:
        with transaction.atomic():
            for stock_item in stock_items_in_department:
                # if not validate_quantity(stock_item['quantity']):
                #     raise Exception('Quantity is less than Zero')

                stock_item_id = stock_item['stock_item_id']
                quantity = stock_item['quantity']

                department_stock = get_or_create_new_department_stock(stock_item_id, department_id)
                if not department_stock:
                    return None

                department_stock.quantity = quantity
                department_stock.save()
                print('department stock overwritten', department_stock)
            # End of for loop
            return True
    except Exception as e:
        print('Error: ', e)
        return False

def add_item_to_department(stock_items_to_add, dept_id):
    '''
        Quantity of stock items to add cannot be negative or zero.
    '''
    try:
        with transaction.atomic():
            for stock_item in stock_items_to_add:

                res = validate_quantity(stock_item['quantity'], negative_allowed=False, zero_allowed=False)
                if not res:
                    raise Exception('Stock quantity should be positive')

                stock_item_id = stock_item['stock_item_id']
                quantity = stock_item['quantity']

                department_stock = get_or_create_new_department_stock(stock_item_id, dept_id)
                if not department_stock:
                    raise Exception('Failed to add department stock')

                department_stock.quantity += quantity
                department_stock.save()
                print('added item to department', department_stock)
            # End of for loop
            return True
    except Exception as e:
        print('Error: ', e)
        return False

def consume_item_from_department(stock_items_to_consume, dept_id):
    '''
        Quantity of stock items to consume cannot be negative or zero.
    '''

    try:
        with transaction.atomic():
            for stock_item in stock_items_to_consume:

                res = validate_quantity(stock_item['quantity'], negative_allowed=False, zero_allowed=False)
                if not res:
                    raise Exception('Stock quantity should be positive')

                stock_item_id = stock_item['stock_item_id']
                quantity = stock_item['quantity']

                department_stock = get_or_create_new_department_stock(stock_item_id, dept_id)
                if not department_stock:
                    raise Exception('Failed to consume department stock')

                department_stock.quantity -= quantity
                department_stock.save()
                print('Consumed item from department', department_stock)
            # End of for loop
            return True
    except Exception as e:
        print('Error: ', e)
        return False

def get_or_create_new_department_stock(stock_item_id, dept_id):
    try:
        department_stock = DepartmentStock.objects.get(stock_item=stock_item_id, \
                                    department=dept_id)
        return department_stock
    except Exception as e:
        print('Error dest dept: ', e)
        print('creating new department stock with quantity 0')
        department_stock = create_department_stock(stock_item_id, dept_id)
        if department_stock:
            print('Created department stock')
            return department_stock
        else:
            return None

def create_purchase_order_draft(item_list, supplier_id, dest_department_id):
    '''
        Requested quantity of item list cannot be negative or zero.
    '''

    try:
        with transaction.atomic():
            purchase_order = PurchaseOrder()
            purchase_order.placed_date = datetime.datetime.now()
            purchase_order.status = PURCHASE_ORDER_STATUS[0][0] # Draft

            purchase_order.supplier = Supplier.objects.get(id=supplier_id)
            purchase_order.dest_department = Department.objects.get(id=dest_department_id)
            purchase_order.save()

            for item in item_list:

                res = validate_quantity(item['requested_quantity'], negative_allowed=False, zero_allowed=False)
                if not res:
                    raise Exception('Stock quantity should be positive')

                purchase_order_item = PurchaseOrderItem()
                purchase_order_item.purchase_order = purchase_order
                purchase_order_item.item = StockItem.objects.get(id=item['stock_item_id'])
                purchase_order_item.requested_quantity = item['requested_quantity']
                if item.get('requested_unit_price'):
                    purchase_order_item.requested_unit_price = item['requested_unit_price']
                purchase_order_item.save()
            # End of for loop

            print('Success create_purchase_order_draft', purchase_order)
            return True
    except Exception as e:
        print('Error in create_purchase_order_draft: ', e)
        return False

def purchase_order_honoured(purchase_order_id, item_list):
    '''
        Received quantity of item list cannot be negative.
    '''

    try:
        with transaction.atomic():
            purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
            if purchase_order.status == PURCHASE_ORDER_STATUS[1][0]: # Canceled
                print('Purchase order is Canceled')
                return None

            if purchase_order.status == PURCHASE_ORDER_STATUS[3][0]: # Complete
                print('Purchase order is already completed')
                return None

            purchase_order.status = PURCHASE_ORDER_STATUS[3][0] # Complete
            purchase_order.honoured_date_ts = datetime.datetime.now()
            purchase_order.save()

            stock_items_to_add = []
            for item in item_list:

                res = validate_quantity(item['received_quantity'], negative_allowed=False, zero_allowed=True)
                if not res:
                    raise Exception('Stock quantity should be positive')

                purchase_order_item = PurchaseOrderItem.objects.get(purchase_order=purchase_order, item=item['stock_item_id'])
                purchase_order_item.received_quantity = item['received_quantity']
                if item.get('received_unit_price'):
                    purchase_order_item.received_unit_price = item['received_unit_price']
                purchase_order_item.save()
                stock_items_to_add.append({"stock_item_id": item['stock_item_id'], "quantity": item['received_quantity']})
            # End of for loop

            res = add_item_to_department(stock_items_to_add, purchase_order.dest_department.id)
            if not res:
                raise Exception('Failed to add stock in department')
            print('Success purchase_order_honoured', purchase_order)
            return True
    except Exception as e:
        print('Error in purchase_order_honoured: ', e)
        return False

def create_stock_transfer_request_draft(source_department_id, dest_department_id, item_list):
    '''
        Quantity of item list cannot be negative or zero.
    '''

    auto_honour_stock_transfer_requests = False
    try:
        bool_string = SystemClientConfig.objects.get(key='auto_honour_stock_transfer_requests').value
        if bool_string.upper() == 'TRUE':
            auto_honour_stock_transfer_requests = True
    except Exception as e:
        print('Error in create_stock_transfer_request_draft, auto_honour_stock_transfer_requests not found: ', e)

    print('create_stock_transfer_request_draft, auto_honour_stock_transfer_requests', auto_honour_stock_transfer_requests)

    # ---------------------------------------------------------------------------------------------
    try:
        with transaction.atomic():
            stock_transfer_request = StockTransferRequest()
            stock_transfer_request.placed_date = datetime.datetime.now()
            stock_transfer_request.status = STOCK_TRANSFER_REQUEST_STATUS[0][0] # Draft

            stock_transfer_request.source_department = Department.objects.get(id=source_department_id)
            stock_transfer_request.dest_department = Department.objects.get(id=dest_department_id)
            stock_transfer_request.save()

            for item in item_list:

                res = validate_quantity(item['requested_quantity'], negative_allowed=False, zero_allowed=False)
                if not res:
                    raise Exception('Stock quantity should be positive')

                stock_transfer_request_item = StockTransferRequestItem()
                stock_transfer_request_item.stock_transfer_request = stock_transfer_request
                stock_transfer_request_item.item = StockItem.objects.get(id=item['stock_item_id'])
                stock_transfer_request_item.requested_quantity = item['requested_quantity']
                stock_transfer_request_item.save()
            # End of for loop

            print('Success create_stock_transfer_request_draft', stock_transfer_request_item)
            if auto_honour_stock_transfer_requests:
                received_stock_item_list = []
                for stock_item in item_list:
                    received_stock_item_list.append({
                        "stock_item_id" : stock_item['stock_item_id'],
                        "received_quantity" : stock_item['requested_quantity']
                    })

                res = stock_transfer_request_honoured(stock_transfer_request.id, received_stock_item_list)
                if res:
                    print('Success auto honoured stock transfer request')
                else:
                    raise Exception('Failed to auto honour stock transfer request')

            return stock_transfer_request
    except Exception as e:
        print('Error in create_stock_transfer_request_draft: ', e)
        return None

def stock_transfer_request_honoured(stock_transfer_request_id, item_list):
    '''
        Quantity of item list cannot be negative.
    '''

    try:
        with transaction.atomic():
            stock_transfer_request = StockTransferRequest.objects.get(id=stock_transfer_request_id)
            if stock_transfer_request.status == STOCK_TRANSFER_REQUEST_STATUS[1][0]: # Canceled
                print('Stock transfer request is Canceled')
                return None

            if stock_transfer_request.status == STOCK_TRANSFER_REQUEST_STATUS[2][0]: # Complete
                print('Stock transfer request is already completed')
                return None

            stock_transfer_request.status = STOCK_TRANSFER_REQUEST_STATUS[2][0] # Complete
            stock_transfer_request.honoured_date_ts = datetime.datetime.now()
            stock_transfer_request.save()

            stock_items_to_transfer = []
            for item in item_list:

                res = validate_quantity(item['received_quantity'], negative_allowed=False, zero_allowed=True)
                if not res:
                    raise Exception('Stock quantity should be positive')

                stock_transfer_request_item = StockTransferRequestItem.objects.get(stock_transfer_request=stock_transfer_request, item=item['stock_item_id'])
                stock_transfer_request_item.received_quantity = item['received_quantity']
                stock_transfer_request_item.save()
                stock_items_to_transfer.append({"stock_item_id": item['stock_item_id'], "quantity": item['received_quantity']})
            # End of for loop

            res = transfer_stock_between_departments(stock_transfer_request.source_department.id, stock_transfer_request.dest_department.id, stock_items_to_transfer)

            if not res:
                raise Exception('Failed to transfer stock between department')
            print('Success stock_transfer_request_honoured', stock_transfer_request)
            return True
    except Exception as e:
        print('Error in stock_transfer_request_honoured: ', e)
        return False


# ----------------------------------------------------------------------------------------------

## output is quantity of an item in all departments
def get_stock_aggregate_from_all_departments(department_stock_item_list):
    total_quantity = 0
    for department_stock_item in department_stock_item_list:
        total_quantity = total_quantity + float(department_stock_item['quantity'])

    return total_quantity


## Output is departmentwise quantity of all items and its total quantity in all departments
def get_stock_report():
    stock_items = StockItem.objects.all()

    stock_item_list = []

    for stock_item in stock_items:
        stock_item_dict = {}
        stock_item_dict['stock_name'] = stock_item.name
        department_stocks = DepartmentStock.objects.filter(stock_item=stock_item)
        department_stock_item_list = []
        for department_stock in department_stocks:
            department_stock_item_list.append({'department': department_stock.department.name, 'quantity': department_stock.quantity})

        stock_item_dict['department_stock_item_list'] = department_stock_item_list

        total_quantity = get_stock_aggregate_from_all_departments(department_stock_item_list)

        stock_item_dict['total_quantity'] = total_quantity

        stock_item_list.append(stock_item_dict)

    print(stock_item_list)

    return stock_item_list

def create_recipe(produced_stock_item_id, produced_item_quantity, ingredients_list):
    '''
        1. Produced item quantity cannot be negative or zero.
        2. Quantity in ingredient list cannot be negative or zero.
    '''

    try:
        with transaction.atomic():
            for ingredients_list_item in ingredients_list:
                res = validate_quantity(ingredients_list_item['quantity'], negative_allowed=False, zero_allowed=False)
                if not res:
                    raise Exception('Ingredient stock quantity should be positive')


            res = validate_quantity(produced_item_quantity, negative_allowed=False, zero_allowed=False)
            if not res:
                raise Exception('Stock quantity should be positive')

            recipe = Recipe()
            recipe.produced_item = StockItem.objects.get(id=produced_stock_item_id)
            recipe.produced_item_quantity = produced_item_quantity
            recipe.ingredients_json = json.dumps(ingredients_list)
            recipe.save()
            print('Saved recipe ', recipe)
            return recipe
    except Exception as e:
        print('Error in create_recipe', e)
        return None

## This function creates a system checkpoint for all the stocks available in department stock
def create_system_verification_checkpoint():
    try:
        with transaction.atomic():
            system_checkpoint = SystemStockVerificationCheckpoint.objects.create(checkpoint_ts=datetime.datetime.now())

            department_stocks = DepartmentStock.objects.all()

            for department_stock in department_stocks:
                kwargs = {}
                kwargs['system_stock_verification_checkpoint'] = system_checkpoint
                kwargs['dept_stock'] = department_stock
                kwargs['quantity'] = department_stock.quantity
                # kwargs['quantity_unit'] = department_stock.stock_item.quantity_unit

                system_stock_verification_checkpoint_item = SystemStockVerificationCheckpointItem.objects.create(**kwargs)
                print(system_stock_verification_checkpoint_item)

        return system_checkpoint
    except Exception as e:
        print(e)
        return None


def create_manual_verification_checkpoint(manaul_verification_items):
    '''
        Quantity of manaul_verification_items cannot be negative.
    '''

    try:
        with transaction.atomic():
            system_checkpoint = create_system_verification_checkpoint()

            if not system_checkpoint:
                raise Exception('Error creating system verification checkpoint')

            manual_checkpoint = ManualStockVerificationCheckpoint.objects.create(checkpoint_ts=datetime.datetime.now(), corresponding_system_checkpoint=system_checkpoint)

            for item in manaul_verification_items:

                res = validate_quantity(item["quantity"], negative_allowed=False, zero_allowed=True)
                if not res:
                    raise Exception('Stock quantity cannot be negative')

                department_stock = get_or_create_new_department_stock(item["stock_item_id"], item["department_id"])

                if not department_stock:
                    raise Exception('Failed to create department stock entry')

                kwargs = {}
                kwargs['manual_stock_verification_checkpoint'] = manual_checkpoint
                kwargs['dept_stock'] = department_stock
                kwargs['quantity'] = item["quantity"]

                manual_stock_verification_checkpoint_item = ManualStockVerificationCheckpointItem.objects.create(**kwargs)
                print(manual_stock_verification_checkpoint_item)

                ## creating stock verification checkpoint report
            res = create_stock_verification_checkpoint_report(manual_checkpoint, system_checkpoint)

            if not res:
                raise Exception('Error creating stock_verification_checkpoint_report')

            return True
    except Exception as e:
        print('create_manual_checkpoint_for_stock_item: ', e)
        return None


def get_sale_item_tax_amount(stock_item, quantity):
    if stock_item.tax_rate:
        return ((stock_item.sale_price * quantity) * stock_item.tax_rate.rate)/100
    else:
        return 0


def get_item_total_amount(stock_item, quantity, item_tax_amount):
    return (stock_item.sale_price * quantity) + item_tax_amount


def create_sale_order_draft(item_list, order_code, order_type, sale_order_department_id=None):
    '''
        1. Quantity of item list cannot be negative or zero.
        2. Duplicate items are not allowed.
    '''

    if not sale_order_department_id:
        try:
            sale_order_department_id = SystemClientConfig.objects.get(key='default_sale_department').value
        except Exception as e:
            print('Error in create_sale_order_draft, default_sale_department not found: ', e)
            return None

    try:
        with transaction.atomic():
            sale_order = SaleOrder()
            sale_order.placed_date = datetime.datetime.now()
            sale_order.order_code = order_code
            sale_order.order_type = order_type
            sale_order.status = SALE_ORDER_STATUS[0][0] # Placed

            sale_order.sale_order_department = Department.objects.get(id=sale_order_department_id)
            sale_order.save()

            for item in item_list:

                res = validate_quantity(item["quantity"], negative_allowed=False, zero_allowed=True)
                if not res:
                    raise Exception('Stock quantity should be positive')

                sale_order_item = SaleOrderItem()
                sale_order_item.sale_order = sale_order
                sale_order_item.item = StockItem.objects.get(id=item['stock_item_id'])
                sale_order_item.quantity = item['quantity']
                sale_order_item.unit_price = sale_order_item.item.sale_price
                sale_order_item.item_tax_rate = sale_order_item.item.tax_rate.rate if sale_order_item.item.tax_rate else 0
                sale_order_item.item_tax_amount = get_sale_item_tax_amount(sale_order_item.item, item['quantity'])

                ## This amount is the total amount of that perticular item in this order
                sale_order_item.item_total_amount = get_item_total_amount(sale_order_item.item, item['quantity'], sale_order_item.item_tax_amount)
                sale_order_item.save()
            # End of for loop

            print('Success sale_order_draft', sale_order)
            return sale_order
    except Exception as e:
        print('Error in create_sale_order_draft: ', e)
        return None


def sale_order_honoured(sale_order_id):
    '''
        Quantity of sale order item list cannot be negative.
    '''

    try:
        with transaction.atomic():
            sale_order = SaleOrder.objects.get(id=sale_order_id)
            if sale_order.status == SALE_ORDER_STATUS[3][0]: # Cancelled
                print('Sale order is Cancelled')
                return None

            if sale_order.status == SALE_ORDER_STATUS[2][0]: # Delivered
                print('Sale order is already completed')
                return None

            total_amount, total_tax_amount = sale_order.calculate_sale_order_totals()

            print('total and tax amount: ', total_amount, total_tax_amount)

            sale_order.total_tax_amount = total_tax_amount
            sale_order.total_amount = total_amount
            sale_order.status = SALE_ORDER_STATUS[2][0] # Delivered
            sale_order.honoured_date_ts = datetime.datetime.now()
            sale_order.save()

            stock_items_to_consume = []
            sale_order_item_list = sale_order.get_items.all()
            for sale_order_item in sale_order_item_list:

                res = validate_quantity(sale_order_item.quantity, negative_allowed=False, zero_allowed=True)
                if not res:
                    raise Exception('Stock quantity cannot be negative')

                stock_items_to_consume.append({"stock_item_id": sale_order_item.item.id, "quantity": sale_order_item.quantity})

            # End of for loop

            res = consume_item_from_department(stock_items_to_consume, sale_order.sale_order_department.id)

            if not res:
                raise Exception('Failed to consume stock in department')
            print('Success sale_order_honoured', sale_order)
            return True
    except Exception as e:
        print('Error in sale_order_honoured: ', e)
        return False


def create_stock_verification_checkpoint_report(manual_checkpoint, system_checkpoint):
    try:
        with transaction.atomic():
            kwargs = {}
            kwargs["system_stock_verification_checkpoint"] = system_checkpoint
            kwargs["manual_stock_verification_checkpoint"] = manual_checkpoint
            stock_verification_checkpoint_report = StockVerificationCheckpointReport.objects.create(**kwargs)

            res = create_stock_verification_checkpoint_report_item(stock_verification_checkpoint_report)

            if not res:
                raise Exception('Error in create_stock_verification_checkpoint_report')

            return True
    except Exception as e:
        print('Error in create_stock_verification_checkpoint_report: ',e)
        return None


def create_stock_verification_checkpoint_report_item(stock_verification_checkpoint_report):
    try:
        with transaction.atomic():
            system_checkpoint = stock_verification_checkpoint_report.system_stock_verification_checkpoint
            manual_checkpoint = stock_verification_checkpoint_report.manual_stock_verification_checkpoint

            system_checkpoint_items = system_checkpoint.get_items.all()
            manual_checkpoint_items = manual_checkpoint.get_items.all()

            kwargs = {}
            for system_checkpoint_item in system_checkpoint_items:
                kwargs.clear()
                item = system_checkpoint_item.dept_stock.stock_item
                department = system_checkpoint_item.dept_stock.department

                corresponding_manual_checkpoint_item = manual_checkpoint_items.filter(dept_stock__stock_item=item, dept_stock__department=department).first()

                kwargs["stock_verification_checkpoint_report"] = stock_verification_checkpoint_report
                kwargs["dept_stock"] = system_checkpoint_item.dept_stock

                if corresponding_manual_checkpoint_item:

                    if corresponding_manual_checkpoint_item.quantity < system_checkpoint_item.quantity:
                        kwargs['status'] = StockVerificationCheckpointReportItem.STATUS[1][0]
                        kwargs['quantity'] = system_checkpoint_item.quantity - corresponding_manual_checkpoint_item.quantity
                    elif corresponding_manual_checkpoint_item.quantity > system_checkpoint_item.quantity:
                        kwargs['status'] = StockVerificationCheckpointReportItem.STATUS[2][0]
                        kwargs['quantity'] = corresponding_manual_checkpoint_item.quantity - system_checkpoint_item.quantity
                    elif corresponding_manual_checkpoint_item.quantity == system_checkpoint_item.quantity:
                        kwargs['status'] = StockVerificationCheckpointReportItem.STATUS[0][0]
                        kwargs['quantity'] = 0
                    else:
                        kwargs['status'] = StockVerificationCheckpointReportItem.STATUS[3][0]
                        kwargs['quantity'] = None

                else:
                    kwargs['status'] = StockVerificationCheckpointReportItem.STATUS[4][0]
                    kwargs['quantity'] = None

                stock_verification_checkpoint_report_item = StockVerificationCheckpointReportItem.objects.create(**kwargs)
            ## End of for loop
            return True
    except Exception as e:
        print('Error in create_stock_verification_checkpoint_report_item: ',e)
        return None
