from __future__ import unicode_literals

from django.db import models

from helper_functions import convert_date_to_epoch


NATURE_TYPE = (
    (1, 'Consumable'), # perishable
    (2, 'Durable'), # non-consumable
)

USAGE_TYPE = (
    (1, 'Raw Material'),
    (2, 'Finished Product'),
    (3, 'Appliance'),
)

QUANTITY_UNIT = (
    (1, 'Kilo Grams'),
    (2, 'Grams'),
    (3, 'Liters'),
    (4, 'Mili Liters'),
    (5, 'Units'),
)

PURCHASE_ORDER_STATUS = (
    (1, 'Draft'),
    (2, 'Canceled'),
    (3, 'Placed'),
    (4, 'Complete'),
)

SALE_ORDER_STATUS = (
    (1, 'Placed'),
    (2, 'In Process'),
    (3, 'Delivered'),
    (4, 'Cancelled')
)

SALE_ORDER_TYPE = (
    (1, 'Parcel'),
    (2, 'Dine'),
    (3, 'Branch Transfer'),
    (4, 'Custom Order'),
    (5, 'Bulk Order'),
)


STOCK_VERIFICATION_CHECKPOINT_TYPE = (
    (1, 'Manually Generated'),
    (2, 'System Generated'),
)

STOCK_TRANSFER_REQUEST_STATUS = (
    (1, 'Draft'),
    (2, 'Cancelled'),
    (3, 'Complete'),
)

# Create your models here.
class StockItem(models.Model):
    code = models.CharField(max_length=20, unique=True, help_text="Unique code to identify Stock Item")
    name = models.CharField(max_length=100, help_text="Name of the Item")
    regional_name = models.CharField(max_length=100, help_text="Regional Name of the Item")
    brand = models.CharField(max_length=100, null=True, blank=True, help_text="Producer company or grade or quality of item")
    regional_brand_name = models.CharField(max_length=100, null=True, blank=True, help_text="Regional Brand Name of the Item")
    sale_price = models.FloatField(default=0.0, help_text="valid in case of usage type: Finished Product -- in Rs.")
    usage_type = models.IntegerField(choices=USAGE_TYPE, default=1)
    nature = models.IntegerField(choices=NATURE_TYPE, null=True, blank=True, default=1)
    quantity_unit = models.IntegerField(choices=QUANTITY_UNIT)
    tax_rate = models.ForeignKey('TaxRate', null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    shelf_life = models.DurationField(null=True, blank=True, help_text='format# days hrs:min:sec OR in sec')
    notes = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        if self.brand:
            return u'%s, %s, %s -- %s' % (self.pk, self.code, self.name, self.brand)
        else:
            return u'%s, %s, %s' % (self.pk, self.code, self.name)

    def get_json(self):
        result = {}
        result["stock_item_id"] = self.id
        result["code"] = self.code if self.code else None
        result["name"] = self.name if self.name else None
        result["regional_name"] = self.regional_name if self.regional_name else None
        result["brand"] = self.brand if self.brand else None
        result["sale_price"] = self.sale_price if self.sale_price else None
        result["usage_type"] = self.usage_type if self.usage_type else None
        result["nature"] = self.nature if self.nature else None
        result["quantity_unit"] = self.quantity_unit if self.quantity_unit else None
        result["quantity_unit_display"] = self.get_quantity_unit_display() if self.quantity_unit else None
        result["tax_rate"] = self.tax_rate.rate if self.tax_rate else None
        result["description"] = self.description if self.description else None
        result["shelf_life"] = self.shelf_life if self.shelf_life else None
        result["notes"] = self.notes if self.notes else None
        result["is_active"] = self.is_active if self.is_active else None
        result["created"] = convert_date_to_epoch(self.created) if self.created else None
        result["last_modified"] = convert_date_to_epoch(self.last_modified) if self.last_modified else None

        result["requested_quantity"] = None # For frontend
        result["received_quantity"] = None # For frontend
        result["requested_unit_price"] = None # For frontend
        result["received_unit_price"] = None # For frontend
        return result


class DepartmentStock(models.Model):
    stock_item = models.ForeignKey('StockItem')
    department = models.ForeignKey('department.Department')
    quantity = models.FloatField(default=1)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('-created',)
        unique_together = ('stock_item', 'department',)

    def __str__(self):
        if self.stock_item.brand:
            return u'%s, %s -- %s, %s' % (self.pk, self.stock_item.name, self.stock_item.brand, self.department.name)
        else:
            return u'%s, %s, %s' % (self.pk, self.stock_item.name, self.department.name)


class TaxRate(models.Model):
    rate = models.FloatField(unique=True)
    # applicable_in_city
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return u'%s, %s' % (self.pk, self.rate)


class Recipe(models.Model):
    # sample recipe procedure field format
    # [
    #     {
    #         "stock_item_id": 5,
    #         "quantity": 1
    #     },
    #     {
    #         "stock_item_id": 4,
    #         "quantity": 1
    #     }
    # ]
    produced_item = models.ForeignKey(StockItem)
    produced_item_quantity = models.FloatField(default=1)

    ingredients_json = models.TextField(help_text='describe the recipe in JSON :)')
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        if self.produced_item.brand:
            return u'%s, %s -- %s' % (self.pk, self.produced_item.name, self.produced_item.brand)
        else:
            return u'%s, %s' % (self.pk, self.produced_item.name)


class PurchaseOrder(models.Model):
    placed_date = models.DateTimeField(help_text='date on which PO was sent to supplier')
    status = models.IntegerField(choices=PURCHASE_ORDER_STATUS, default=1)

    supplier = models.ForeignKey('supplier.Supplier')
    dest_department = models.ForeignKey('department.Department', help_text='department to which stock should be added if purchase order is complete')

    honoured_date_ts = models.DateTimeField(null=True, blank=True, help_text='date on which goods against PO were delivered correctly')
    cancelled_date_ts = models.DateTimeField(null=True, blank=True, help_text='date on which PO was cancelled')

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def get_json(self, limited_fields=False):
        result = {}
        result["purchase_order_id"] = self.id
        result["placed_date"] = convert_date_to_epoch(self.placed_date) if self.placed_date else None
        result["status"] = self.status if self.status else None
        result["status_display"] = self.get_status_display() if self.status else None
        result["supplier"] = self.supplier.get_json() if self.supplier else None
        result["dest_department"] = self.dest_department.get_json() if self.dest_department else None
        result["honoured_date_ts"] = convert_date_to_epoch(self.honoured_date_ts) if self.honoured_date_ts else None
        result["cancelled_date_ts"] = convert_date_to_epoch(self.cancelled_date_ts) if self.cancelled_date_ts else None
        result["created"] = convert_date_to_epoch(self.created) if self.created else None
        result["last_modified"] = convert_date_to_epoch(self.last_modified) if self.last_modified else None
        if not limited_fields:
            result["purchase_order_items"] = [x.get_json() for x in self.get_purchase_order_items.all()]
        return result

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return u'%s, %s -- %s' % (self.pk, self.supplier.name, self.placed_date)


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey('PurchaseOrder', help_text='Select purchase order', related_name='get_purchase_order_items')
    item = models.ForeignKey('StockItem', help_text='Select the item to include in purchase order')

    requested_quantity = models.FloatField(default=1)
    requested_unit_price = models.FloatField(default=0.0, help_text="Expected price per unit item -- at time of placing order -- in Rs.")

    received_quantity = models.FloatField(null=True, blank=True)
    received_unit_price = models.FloatField(null=True, blank=True, help_text="actual price charged by supplier per unit item -- at time of purchase -- in Rs.")

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def get_json(self):
        result = {}
        result["purchase_order_item_id"] = self.id
        result["purchase_order_id"] = self.purchase_order.id

        result["stock_item"] = self.item.get_json() if self.item else None
        result["requested_quantity"] = self.requested_quantity if self.requested_quantity else None
        result["requested_unit_price"] = self.requested_unit_price if self.requested_unit_price else None
        result["received_quantity"] = self.received_quantity if self.received_quantity else None
        result["received_unit_price"] = self.received_unit_price if self.received_unit_price else None

        result["created"] = convert_date_to_epoch(self.created) if self.created else None
        result["last_modified"] = convert_date_to_epoch(self.last_modified) if self.last_modified else None
        return result

    class Meta:
        ordering = ('-created',)
        unique_together = ('purchase_order', 'item',)

    def __str__(self):
        if self.item.brand:
            return u'%s, PO: %s, %s -- %s' % (self.pk, self.purchase_order, self.item.name, self.item.brand)
        else:
            return u'%s, PO: %s, %s' % (self.pk, self.purchase_order, self.item.name)


class SaleOrder(models.Model):
    order_code = models.CharField(max_length=25, null=True, blank=True, help_text='can keep daily order_code separate from PK')
    placed_date = models.DateTimeField(help_text='date on which sale took place') # provision if backdated sale entries have to be made
    order_type = models.IntegerField(choices=SALE_ORDER_TYPE, default=1)
    status = models.IntegerField(choices=SALE_ORDER_STATUS, default=1)

    total_discount_amount = models.FloatField(default=-1, help_text="Total discount on the order in Rs.")
    total_tax_amount = models.FloatField(default=-1, help_text="Total tax on the order in Rs.")
    total_amount = models.FloatField(default=-1, help_text="Total order amount after discount and tax in Rs.")

    sale_order_department = models.ForeignKey('department.Department', help_text='department from which stock should be removed if sale order is complete')

    cancellation_reason = models.TextField(null=True, blank=True, help_text='If order is cancelled. mention the reason here.')

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return u'%s, -- %s' % (self.pk, self.placed_date)

    def calculate_sale_order_totals(self):
        tax_amount = 0
        total_amount = 0
        total_amount_without_tax = 0

        order_items = self.get_items.all()
        for order_item in order_items:
            tax_amount = tax_amount + ((order_item.item.sale_price * order_item.quantity) * order_item.item_tax_rate)/100
            total_amount_without_tax = total_amount_without_tax + (order_item.item.sale_price * order_item.quantity)

        total_amount = total_amount_without_tax + tax_amount

        return total_amount, tax_amount


class SaleOrderItem(models.Model):
    sale_order = models.ForeignKey('SaleOrder', help_text='Select Sale order', related_name='get_items')
    item = models.ForeignKey('StockItem', help_text='Select the item to include in Sale order')

    quantity = models.FloatField(default=1)
    unit_price = models.FloatField(default=0.0, help_text="Sale price per unit item -- at time of sale -- in Rs.")

    item_discount_amount = models.FloatField(default=0.0, help_text="Total discount for current item in Rs.")
    item_tax_rate = models.FloatField(default=0.0, help_text="Tax rate for current item in %.")
    item_tax_amount = models.FloatField(default=0.0, help_text="Total tax for current item in Rs.")
    item_total_amount = models.FloatField(default=0.0, help_text="Total item amount after discount and tax in Rs.")

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('-created',)
        unique_together = ('sale_order', 'item',)

    def __str__(self):
        if self.item.brand:
            return u'%s, PO: %s, %s -- %s' % (self.pk, self.sale_order, self.item.name, self.item.brand)
        else:
            return u'%s, PO: %s, %s' % (self.pk, self.sale_order, self.item.name)

class StockTransferRequest(models.Model):
    placed_date = models.DateTimeField(help_text='date on which STR was sent')
    status = models.IntegerField(choices=STOCK_TRANSFER_REQUEST_STATUS, default=1)

    source_department = models.ForeignKey('department.Department', help_text='department from which stock should be refuced.', related_name='source_stock_requests')
    dest_department = models.ForeignKey('department.Department', help_text='department to which stock should be added.', related_name='dest_stock_requests')

    honoured_date_ts = models.DateTimeField(null=True, blank=True, help_text='date on which goods against STR were delivered correctly')
    cancelled_date_ts = models.DateTimeField(null=True, blank=True, help_text='date on which STR was cancelled')

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def get_json(self, limited_fields=False):
        result = {}
        result["stock_transfer_request_id"] = self.id
        result["placed_date"] = convert_date_to_epoch(self.placed_date) if self.placed_date else None
        result["status"] = self.status if self.status else None
        result["status_display"] = self.get_status_display() if self.status else None
        result["source_department"] = self.source_department.get_json() if self.source_department else None
        result["dest_department"] = self.dest_department.get_json() if self.dest_department else None
        result["honoured_date_ts"] = convert_date_to_epoch(self.honoured_date_ts) if self.honoured_date_ts else None
        result["cancelled_date_ts"] = convert_date_to_epoch(self.cancelled_date_ts) if self.cancelled_date_ts else None
        result["created"] = convert_date_to_epoch(self.created) if self.created else None
        result["last_modified"] = convert_date_to_epoch(self.last_modified) if self.last_modified else None
        if not limited_fields:
            result["stock_transfer_request_items"] = [x.get_json() for x in self.get_stock_transfer_request_items.all()]
        return result

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return u'%s, %s' % (self.pk, self.placed_date)


class StockTransferRequestItem(models.Model):
    stock_transfer_request = models.ForeignKey('StockTransferRequest', related_name='get_stock_transfer_request_items', help_text='Select stock transfer request')
    item = models.ForeignKey('StockItem', help_text='Select the item to include in stock transfer request')

    requested_quantity = models.FloatField(default=1)
    received_quantity = models.FloatField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def get_json(self):
        result = {}
        result["stock_transfer_request_item_id"] = self.id
        result["stock_transfer_request_id"] = self.stock_transfer_request.id

        result["stock_item"] = self.item.get_json() if self.item else None
        result["requested_quantity"] = self.requested_quantity if self.requested_quantity else None
        result["received_quantity"] = self.received_quantity if self.received_quantity else None

        result["created"] = convert_date_to_epoch(self.created) if self.created else None
        result["last_modified"] = convert_date_to_epoch(self.last_modified) if self.last_modified else None
        return result

    class Meta:
        ordering = ('-created',)
        unique_together = ('stock_transfer_request', 'item',)

    def __str__(self):
        if self.item.brand:
            return u'%s, PO: %s, %s -- %s' % (self.pk, self.stock_transfer_request, self.item.name, self.item.brand)
        else:
            return u'%s, PO: %s, %s' % (self.pk, self.stock_transfer_request, self.item.name)


class SystemStockVerificationCheckpoint(models.Model):
    '''
    when user will enter mnual sotck values at the end of each month and will click verity/compare, system will automatically
    generate checkpoint of verification_type = "System Genetated" with reference to manual checkpoint against which user
    intends to verify
    '''

    checkpoint_ts = models.DateTimeField(help_text='date of stock verification checkpoint')

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return u'%s, %s' % (self.pk, self.checkpoint_ts)

class SystemStockVerificationCheckpointItem(models.Model):
    system_stock_verification_checkpoint = models.ForeignKey('SystemStockVerificationCheckpoint', related_name='get_items', help_text='Select system stock verification checkpoint')
    dept_stock = models.ForeignKey('DepartmentStock', help_text='Select the stock item in dept to include in SystemStockVerificationCheckpoint')
    quantity = models.FloatField(default=1, help_text='Quantity of item found during verification')

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        if self.dept_stock.stock_item.brand:
            # SCP -- system checkpoint
            return u'%s, SSVC: %s, %s -- %s' % (self.pk, self.system_stock_verification_checkpoint, self.dept_stock.stock_item.name, self.dept_stock.stock_item.brand)
        else:
            return u'%s, SSVC: %s, %s' % (self.pk, self.system_stock_verification_checkpoint, self.dept_stock.stock_item.name)

class ManualStockVerificationCheckpoint(models.Model):
    '''
    when user will enter mnual sotck values at the end of each month and will click verity/compare, system will automatically
    generate checkpoint of verification_type = "System Genetated" with reference to manual checkpoint against which user
    intends to verify
    '''

    corresponding_system_checkpoint = models.OneToOneField('SystemStockVerificationCheckpoint', help_text="will contain manual checkpoint reference if current checkpoint is system generated else it will be null. This reference will be used to compare system checkpoint with corresponding manual checkpoint")
    checkpoint_ts = models.DateTimeField(help_text='date of stock verification checkpoint')

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return u'%s, %s' % (self.pk, self.checkpoint_ts)

class ManualStockVerificationCheckpointItem(models.Model):
    manual_stock_verification_checkpoint = models.ForeignKey('ManualStockVerificationCheckpoint', related_name='get_items', help_text='Select manual stock verification checkpoint')
    dept_stock = models.ForeignKey('DepartmentStock', help_text='Select the stock item in dept to include in ManualStockVerificationCheckpoint')
    quantity = models.FloatField(default=1, help_text='Quantity of item found during verification')

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        if self.dept_stock.stock_item.brand:
            # SCP -- system checkpoint
            return u'%s, MSVC: %s, %s -- %s' % (self.pk, self.manual_stock_verification_checkpoint, self.dept_stock.stock_item.name, self.dept_stock.stock_item.brand)
        else:
            return u'%s, MSVC: %s, %s' % (self.pk, self.manual_stock_verification_checkpoint, self.dept_stock.stock_item.name)

class StockVerificationCheckpointReport(models.Model):
    system_stock_verification_checkpoint = models.OneToOneField('SystemStockVerificationCheckpoint', help_text='Select system stock verification checkpoint')
    manual_stock_verification_checkpoint = models.OneToOneField('ManualStockVerificationCheckpoint', help_text='Select manual stock verification checkpoint')

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return u'SVC Report: %s, System SVC: %s, Manual SVC: %s' % (self.pk, self.system_stock_verification_checkpoint.id, self.manual_stock_verification_checkpoint.id)

class StockVerificationCheckpointReportItem(models.Model):
    STATUS = (
        (0, 'Equal'),
        (1, 'Short'),
        (2, 'Excess'),
        (3, 'Inconsistent data'),
        (4, 'Manual stock not found'),
    )

    stock_verification_checkpoint_report = models.ForeignKey('StockVerificationCheckpointReport', help_text='Select stock verification checkpoint report')
    dept_stock = models.ForeignKey('DepartmentStock', help_text='Select the stock item in dept to include in stock verification checkpoint report')
    quantity = models.FloatField(default=None, null=True, blank=True, help_text='Quantity of item found during verification')
    status = models.IntegerField(choices=STATUS, default=1)
    notes = models.TextField(max_length=100, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return u'%s, %s, %s, %s' % (self.pk, self.stock_verification_checkpoint_report, self.dept_stock.stock_item.name, self.status)
