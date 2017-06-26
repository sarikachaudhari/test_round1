from django.contrib import admin
from .models import *
# Register your models here.
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'code',
        'name',
        'address',
        'city',
        'state',
    )
    list_filter = (
        'city',
        'state',
    )
    search_fields = (
        'id',
        'code',
        'name',
    )
admin.site.register(Supplier, SupplierAdmin)
