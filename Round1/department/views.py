import json
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.db.models import Q
from .models import Department
from helper_functions import get_params

# Create your views here.

def get_all_departments(request):

    department_list = []

    for dept in Department.objects.all():
        department_list.append(dept.get_json())
    return JsonResponse({"data": department_list, "status": True})

def add_department(request):
    params = get_params(request)
    department_name = params.get('department_name')

    if not department_name:
        return JsonResponse({"validation": "department name not found", "status": False})

    try:
        dept = Department()
        dept.name = department_name
        dept.save()
        return JsonResponse({"validation": "Department added successfully", "status": True})
    except Exception as e:
        print('Error in add_department: ',e)
        return JsonResponse({"validation": "Failed to add department", "status": False})
