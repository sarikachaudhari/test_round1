from django.contrib import admin
from .models import *

# Register your models here.
class DepartmentStockAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_stockitem_name',
        'get_department_name',
        'quantity',
        'get_quantity_unit',
    )
    list_filter = (
        'department__name',
        'stock_item',
    )
    search_fields = (
        'id',
        'department__name',
        'stock_item__name',
        'stock_item__brand',
        'stock_item__code',
    )

    def get_quantity_unit(self, obj):
        return u'%s, %s' % (obj.stock_item.quantity_unit, obj.stock_item.get_quantity_unit_display())

    def get_stockitem_name(self, obj):
        if(obj.stock_item.brand):
            return u'%s, %s -- %s' % (obj.stock_item.id, obj.stock_item.name, obj.stock_item.brand)
        else:
            return u'%s, %s' % (obj.stock_item.id, obj.stock_item.name)

    def get_department_name(self, obj):
        return u'%s, %s' % (obj.department.id, obj.department.name)

admin.site.register(DepartmentStock, DepartmentStockAdmin)


class StockItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'code',
        'name',
        'regional_name',
        'usage_type',
        'sale_price',
        'quantity_unit',
        'is_active',
    )
    list_filter = (
        'usage_type',
        'nature',
        'is_active'
    )
    search_fields = (
        'id',
        'code',
        'name',
    )
admin.site.register(StockItem, StockItemAdmin)


class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'placed_date',
        'supplier',
        'get_department_name',
        'status',
    )
    list_filter = (
        'status',
        'placed_date',
        'supplier__name',
    )
    search_fields = (
        'id',
    )

    def get_department_name(self, obj):
        return u'%s, %s' % (obj.dest_department.id, obj.dest_department.name)

admin.site.register(PurchaseOrder, PurchaseOrderAdmin)


class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'purchase_order',
        'get_item_name',
        'requested_unit_price',
        'requested_quantity',
        'get_quantity_unit',
        'received_unit_price',
        'received_quantity',
        'get_quantity_unit',
    )

    search_fields = (
        'purchase_order__id',
        'item__name'
    )

    def get_quantity_unit(self, obj):
        return u'%s, %s' % (obj.item.quantity_unit, obj.item.get_quantity_unit_display())

    def get_item_name(self, obj):
        if(obj.item.brand):
            return u'%s, %s -- %s' % (obj.item.id, obj.item.name, obj.item.brand)
        else:
            return u'%s, %s' % (obj.item.id, obj.item.name)
admin.site.register(PurchaseOrderItem, PurchaseOrderItemAdmin)


class SaleOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'placed_date',
        'order_type',
        'status',
        'total_discount_amount',
        'total_tax_amount',
        'total_amount',
    )
    list_filter = (
        'status',
        'placed_date',
        'order_type',
    )
    search_fields = (
        'id',
    )

admin.site.register(SaleOrder, SaleOrderAdmin)


class SaleOrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'sale_order',
        'get_item_name',
        'quantity',
        'get_quantity_unit',
        'unit_price',
        'item_discount_amount',
        'item_tax_rate',
        'item_tax_amount',
        'item_total_amount',
    )

    search_fields = (
        'sale_order__id',
        'item__name'
    )

    def get_quantity_unit(self, obj):
        return u'%s, %s' % (obj.item.quantity_unit, obj.item.get_quantity_unit_display())

    def get_item_name(self, obj):
        if(obj.item.brand):
            return u'%s, %s -- %s' % (obj.item.id, obj.item.name, obj.item.brand)
        else:
            return u'%s, %s' % (obj.item.id, obj.item.name)
admin.site.register(SaleOrderItem, SaleOrderItemAdmin)

class StockTransferRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'placed_date',
        'get_source_department_name',
        'get_dest_department_name',
        'status',
    )
    list_filter = (
        'status',
        'placed_date',
    )
    search_fields = (
        'id',
    )

    def get_source_department_name(self, obj):
        return u'%s, %s' % (obj.source_department.id, obj.source_department.name)

    def get_dest_department_name(self, obj):
        return u'%s, %s' % (obj.dest_department.id, obj.dest_department.name)

admin.site.register(StockTransferRequest, StockTransferRequestAdmin)


class StockTransferRequestItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'stock_transfer_request',
        'get_item_name',
        'requested_quantity',
        'get_quantity_unit',
        'received_quantity',
        'get_quantity_unit',
    )

    search_fields = (
        'stock_transfer_request__id',
        'item__name'
    )

    def get_quantity_unit(self, obj):
        return u'%s, %s' % (obj.item.quantity_unit, obj.item.get_quantity_unit_display())

    def get_item_name(self, obj):
        if(obj.item.brand):
            return u'%s, %s -- %s' % (obj.item.id, obj.item.name, obj.item.brand)
        else:
            return u'%s, %s' % (obj.item.id, obj.item.name)
admin.site.register(StockTransferRequestItem, StockTransferRequestItemAdmin)


class SystemStockVerificationCheckpointItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'system_stock_verification_checkpoint',
        'dept_stock',
        'quantity',
        'get_quantity_unit',
    )

    search_fields = (
        'system_stock_verification_checkpoint__id',
    )

    list_filter = (
        'system_stock_verification_checkpoint__checkpoint_ts',
        'dept_stock',
    )

    def get_quantity_unit(self, obj):
        return u'%s, %s' % (obj.dept_stock.stock_item.quantity_unit, obj.dept_stock.stock_item.get_quantity_unit_display())

admin.site.register(SystemStockVerificationCheckpointItem, SystemStockVerificationCheckpointItemAdmin)


class ManualStockVerificationCheckpointItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'manual_stock_verification_checkpoint',
        'dept_stock',
        'quantity',
        'get_quantity_unit',
    )

    search_fields = (
        'manual_stock_verification_checkpoint__id',
    )

    list_filter = (
        'manual_stock_verification_checkpoint__checkpoint_ts',
        'dept_stock',
    )

    def get_quantity_unit(self, obj):
        return u'%s, %s' % (obj.dept_stock.stock_item.quantity_unit, obj.dept_stock.stock_item.get_quantity_unit_display())

admin.site.register(ManualStockVerificationCheckpointItem, ManualStockVerificationCheckpointItemAdmin)


class StockVerificationCheckpointReportItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'stock_verification_checkpoint_report',
        'dept_stock',
        'get_manual_quantity',
        'get_system_quantity',
        'quantity',
        'status',
    )

    search_fields = (
        'stock_verification_checkpoint_report__id',
    )

    list_filter = (
        'stock_verification_checkpoint_report__created',
        'dept_stock__department',
        'status',
    )

    def get_quantity_unit(self, obj):
        return u'%s, %s' % (obj.dept_stock.stock_item.quantity_unit, obj.dept_stock.stock_item.get_quantity_unit_display())

    def get_manual_quantity(self, obj):
        kwargs = {}
        kwargs["dept_stock"] = obj.dept_stock
        kwargs["manual_stock_verification_checkpoint"] = obj.stock_verification_checkpoint_report.manual_stock_verification_checkpoint
        manual_stock_verification_checkpoint_item = ManualStockVerificationCheckpointItem.objects.filter(**kwargs).first()

        if manual_stock_verification_checkpoint_item:
            quantity = manual_stock_verification_checkpoint_item.quantity
        else:
            quantity = None

        return u'%s' % (quantity)

    def get_system_quantity(self, obj):
        kwargs = {}
        kwargs["dept_stock"] = obj.dept_stock
        kwargs["system_stock_verification_checkpoint"] = obj.stock_verification_checkpoint_report.system_stock_verification_checkpoint
        system_stock_verification_checkpoint_item = SystemStockVerificationCheckpointItem.objects.filter(**kwargs).first()

        if system_stock_verification_checkpoint_item:
            quantity = system_stock_verification_checkpoint_item.quantity
        else:
            quantity = None

        return u'%s' % (quantity)


admin.site.register(StockVerificationCheckpointReportItem, StockVerificationCheckpointReportItemAdmin)



###################################################################################
###################################################################################

admin.site.register(TaxRate)
admin.site.register(Recipe)
admin.site.register(ManualStockVerificationCheckpoint)
admin.site.register(SystemStockVerificationCheckpoint)
admin.site.register(StockVerificationCheckpointReport)
