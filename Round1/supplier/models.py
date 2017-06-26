from __future__ import unicode_literals

from django.db import models
from helper_functions import convert_date_to_epoch

# Create your models here.
class Supplier(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def get_json(self):
        result = {}
        result["supplier_id"] = self.id
        result["code"] = self.code if self.code else None
        result["name"] = self.name if self.name else None
        result["address"] = self.address if self.address else None
        result["city"] = self.city if self.city else None
        result["state"] = self.state if self.state else None
        result["created"] = convert_date_to_epoch(self.created) if self.created else None
        result["last_modified"] = convert_date_to_epoch(self.last_modified) if self.last_modified else None
        return result

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return u'%s, %s, %s' % (self.pk, self.code, self.name)

