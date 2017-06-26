import json
from django.shortcuts import render , get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.db.models import Q

from .models import \
    StockItem, \
    SaleOrder, \
    PurchaseOrder, \
    StockTransferRequest

from department.models import Department

# --------------pc------------------------
from .helper_functions import \
    create_stock_transfer_request_draft, \
    create_purchase_order_draft, \
    purchase_order_honoured, \
    produce_items_with_recipe_and_transfer
# --------------aw----------------------------
from .helper_functions import \
    create_sale_order_draft, \
    sale_order_honoured, \
    create_manual_verification_checkpoint, \
    create_recipe

#---------------pc---------------------------
from .validation_helper import \
    validate_stock_item, \
    validate_stock_transfer_request, \
    validate_purchase_order, \
    validate_produce_finished_item
# --------------aw----------------------------
from .validation_helper import \
    validate_sale_order, \
    validate_mark_purchase_order_completed, \
    validate_manual_stock_verification_checkpoint, \
    validate_recipe

from Round1.helper_functions import \
    get_params, \
    convert_date_to_epoch

# Create your views here.


def get_all_stock_items(request):
    '''
        NAME: get_all_stock_items

        expected inputs:
        usage_types = [1,2,3]

        Workflow: This function takes an usage_types input which will be a comma separated string,
        each element considered as usage type of stock item. Function will return all the stock items,
        which are active and usage_types is same as any of input usage_types.
    '''
    try:
        params = get_params(request)
        usage_types = params.get('usage_types')
    except Exception as e:
        print(e)
        return JsonResponse({"validation": "Inconsistent data" , "status": True})

    kwargs = {}
    kwargs["is_active"] = True
    kwargs["usage_type__in"] = usage_types

    stock_items = StockItem.objects.filter(**kwargs)

    stock_item_list = []
    for stock_item in stock_items:
        stock_item_list.append(stock_item.get_json())

    return JsonResponse({"data": stock_item_list, "status": True})

def get_stock_items_for_sale(request):

    kwargs = {}
    kwargs["is_active"] = True
    kwargs["usage_type__in"] = [2] # Finished Product

    stock_items = StockItem.objects.filter(**kwargs)

    stock_item_list = []
    for stock_item in stock_items:
        stock_item_list.append(stock_item.get_json())

    return JsonResponse({"data": stock_item_list, "status": True})

def save_stock_transfer_request(request):
    params = get_params(request)

    status, data, message = validate_stock_transfer_request(params)

    if status:
        res = create_stock_transfer_request_draft(data['source_dept_id'], data['dest_dept_id'], data['stock_item_list'])
        if res:
            return JsonResponse({"validation": "Successfully added stock transfer request", "status": True})
        else:
            return JsonResponse({"validation": "Failed to add stock transfer request", "status": False})
    else:
        return JsonResponse({"validation": message, "status": status})

def get_stock_transfer_request(request):
    params = get_params(request)
    stock_transfer_request_id = params.get('stock_transfer_request_id')

    if not stock_transfer_request_id:
        return JsonResponse({"validation": "Stock transfer request id not found", "status": False})

    try:
        stock_transfer_request = StockTransferRequest.objects.get(id=stock_transfer_request_id)
        data = stock_transfer_request.get_json()
        data.update({"item_list" : []})

        for item in stock_transfer_request.get_stock_transfer_request_items.all():
            stock_item = item.item.get_json()
            stock_item.update({
                "requested_quantity": item.requested_quantity,
                "received_quantity": item.received_quantity,
            })

            data['item_list'].append(stock_item)
        # End of for loop
        return JsonResponse({"data": data, "status": True})
    except Exception as e:
        print('Error in get_stock_transfer_request: ', e)
        return JsonResponse({"validation": "Failed to get stock transfer request", "status": False})

def get_all_stock_transfer_requests(request):

    try:
        stock_transfer_requests = StockTransferRequest.objects.all()
        stock_transfer_requests_list = []
        for stock_transfer_request in stock_transfer_requests:
            stock_transfer_requests_list.append(stock_transfer_request.get_json(limited_fields=True))

        return JsonResponse({"data": stock_transfer_requests_list, "status": True})
    except Exception as e:
        print('Error in get_all_stock_transfer_requests: ', e)
        return JsonResponse({"validation": "Failed to get stock transfer requests", "status": False})

def save_purchase_order(request):
    params = get_params(request)

    status, data, message = validate_purchase_order(params)

    if status:
        res = create_purchase_order_draft(data['item_list'], data['supplier_id'], data['dest_department_id'])
        if res:
            return JsonResponse({"validation": "Successfully saved purchase order", "status": True})
        else:
            return JsonResponse({"validation": "Failed to save purchase order", "status": False})
    else:
        return JsonResponse({"validation": message, "status": False})

def get_purchase_order(request):
    params = get_params(request)
    purchase_order_id = params.get('purchase_order_id')

    if not purchase_order_id:
        return JsonResponse({"validation": "Purchase order id not found", "status": False})

    try:
        purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
        data = purchase_order.get_json()
        data.update({"item_list": []})

        for item in purchase_order.get_purchase_order_items.all():
            stock_item = item.item.get_json()
            stock_item.update({
                "requested_quantity": item.requested_quantity,
                "requested_unit_price": item.requested_unit_price,
                "received_quantity": item.received_quantity,
                "received_unit_price": item.received_unit_price
            })

            data['item_list'].append(stock_item)
        # End of for loop
        return JsonResponse({"data": data, "status": True})
    except Exception as e:
        print('Error in get_purchase_order: ', e)
        return JsonResponse({"validation": "Failed to get purchase order", "status": False})

def get_all_purchase_orders(request):

    try:
        purchase_orders = PurchaseOrder.objects.all()
        purchase_orders_list = []
        for purchase_order in purchase_orders:
            purchase_orders_list.append(purchase_order.get_json(limited_fields=True))

        return JsonResponse({"data": purchase_orders_list, "status": True})
    except Exception as e:
        print('Error in get_all_purchase_orders: ', e)
        return JsonResponse({"validation": "Failed to get purchase orders", "status": False})

def mark_purchase_order_completed(request):
    params = get_params(request)

    status, data, message = validate_mark_purchase_order_completed(params)

    if status:
        res = purchase_order_honoured(data['purchase_order_id'], data['item_list'])
        if res:
            return JsonResponse({"validation": "Purchase order completed", "status": True})
        else:
            return JsonResponse({"validation": "Failed to mark purchase order as complete", "status": False})
    else:
        return JsonResponse({"validation": message, "status": False})

def save_stock_item(request):
    params = get_params(request)

    data, message, status = validate_stock_item(params)

    if status:
        try:
            stock_item = StockItem.objects.create(**data)
            return JsonResponse({"validation": message, "status": status})
        except Exception as e:
            print(e)
            return JsonResponse({"validation": "Inconsistent data: "+e , "status": False})
    else:
        return JsonResponse({"validation": message, "status": status})


def save_sale_order(request):
    params = get_params(request)

    status, data, message = validate_sale_order(params)

    if not status:
        return JsonResponse({"validation": message, "status": status})

    sale_order = create_sale_order_draft(data['item_list'], data['order_code'], data['order_type'])

    if not isinstance(sale_order, SaleOrder):
        print('sale_order: ', sale_order)
        return JsonResponse({"validation": "Failed to save sale order", "status": False})

    if not sale_order_honoured(sale_order.id):
        return JsonResponse({"validation": "Failed to save sale order", "status": False})

    return JsonResponse({"validation": "Sale order placed successfully", "status": True})

def save_recipe(request):
    params = get_params(request)

    status, data, message = validate_recipe(params)

    if not status:
        return JsonResponse({"validation": message, "status": status})

    res = create_recipe(data['produced_stock_item_id'], data['produced_item_quantity'], data['ingredients_list'])
    if res:
        return JsonResponse({"validation": "Recipe saved", "status": True})
    else:
        return JsonResponse({"validation": "Failed to save recipe", "status": False})

def produce_finished_items(request):
    params = get_params(request)

    status, data, message = validate_produce_finished_item(params)

    if not status:
        return JsonResponse({"validation": message, "status": status})

    res = produce_items_with_recipe_and_transfer(data['produced_stock_items'], data['department_id'])
    if res:
        return JsonResponse({"validation": "Stock item is produced", "status": True})
    else:
        return JsonResponse({"validation": "Failed to produce item", "status": False})

# ---------------------------- aw ----------------------------


def manual_stock_verification(request):
    params = get_params(request)

    status, data, message = validate_manual_stock_verification_checkpoint(params['manaul_verification_data'])

    if not status:
        return JsonResponse({"validation": message, "status": status})

    res = create_manual_verification_checkpoint(data)

    print(res)
    if not res:
        return JsonResponse({"validation": "Failed to create manual stock verificaion checkpoint", "status": False})

    return JsonResponse({"validation": "Created manual stock verificaion checkpoint", "status": True})


def current_recipe(request,id=None):
    produced_item = get_object_or_404(Recipe,id=id)
    specific_item = Recipe.objects.filter(produced_item=produced_item)