from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from asset.models import QUANTITY_UNIT,StockItem
from department.models import Department

TRANSACTION_STATUS = (
    (1,'Completed'),
    (2,'Queued'),
    (3,'Failed')
)

# Create your models here.
class Transaction(models.Model):

    created_by = models.ForeignKey(User)
    source_dept = models.ForeignKey(Department, verbose_name = 'Source Department', related_name='source_dept')
    dest_dept = models.ForeignKey(Department, verbose_name = 'Destination Department', related_name='dest_dept')
    stock_item = models.ForeignKey(StockItem)
    quantity = models.FloatField(default=0)
    quantity_unit = models.IntegerField(choices=QUANTITY_UNIT)
    status = models.IntegerField(choices=TRANSACTION_STATUS, default=2)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return u'%s, %s, %s, %s' % (self.source_dept.name, self.dest_dept.name, self.item.name, self.quantity)
