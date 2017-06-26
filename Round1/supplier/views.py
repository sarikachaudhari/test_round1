import json
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.db.models import Q
from .models import Supplier
from helper_functions import get_params

# Create your views here.

def get_all_suppliers(request):

    supplier_list = []

    for supplier in Supplier.objects.all():
        supplier_list.append(supplier.get_json())
    return JsonResponse({"data": supplier_list, "status": True})

def add_supplier(request):
    params = get_params(request)
    code = params.get('code')
    name = params.get('name')
    address = params.get('address')
    city = params.get('city')
    state = params.get('state')

    if not code:
        return JsonResponse({"validation": "Supplier code not found", "status": False})

    if Supplier.objects.filter(code=code).exists():
        return JsonResponse({"validation": "Supplier code already exists", "status": False})

    if not name:
        return JsonResponse({"validation": "Supplier name not found", "status": False})

    try:
        supplier = Supplier()
        supplier.code = code
        supplier.name = name
        if address:
            supplier.address = address
        if city:
            supplier.city = city
        if state:
            supplier.state = state
        supplier.save()
        return JsonResponse({"validation": "Supplier added successfully", "status": True})
    except Exception as e:
        print('Error in add_supplier: ',e)
        return JsonResponse({"validation": "Failed to add supplier", "status": False})
