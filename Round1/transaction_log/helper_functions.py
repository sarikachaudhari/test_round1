import datetime, csv, json
from django.contrib.auth.models import User, Group
from asset.models import *
from supplier.models import *
from department.models import *
from .models import *

from django.db import transaction, IntegrityError
from django.db.models import Q, Max

def create_transaction(created_by, source_dept_id, dest_dept_id, quantity_unit, stock_item_id, status):
    print('Function: Create transaction entry in transcation_log corresponding to a transcation ============================')
    '''
    create_transaction = {
        created_by: user,
        source_dept_id: 2,
        dest_dept_id: 3,
        stock_item_id: 2,
        quantity: 2,
        status: 1,
    }
    '''
    try:
        transaction = Transcation()
        created_by = user
        source_dept = Department.objects.get(id=source_dept_id)
        dest_dept = Department.objects.get(id=dest_dept_id)
        stock_item = StockItem.objects.get(id=stock_item_id)
        quantity = quantity
        quantity_unit = stock_item.quantity_unit
        status = status
        print('success: Transcation created!')
        print('------------------------------')
        return True

    except Exception as e:
        print(e)
        return False
