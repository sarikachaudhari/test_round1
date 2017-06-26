from __future__ import unicode_literals

from django.db import models
from helper_functions import convert_date_to_epoch

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # is_default_for_stock_addition = models.NullBooleanField(help_text='is the current department default to add stock from purchase order. If purchase department does not mention dest_department this will be used to add stock in particular department.');
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def get_json(self):
        result = {}
        result["id"] = self.id
        result["name"] = self.name if self.name else None
        result["created"] = convert_date_to_epoch(self.created) if self.created else None
        result["last_modified"] = convert_date_to_epoch(self.last_modified) if self.last_modified else None
        return result

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return u'%s, %s' % (self.pk, self.name)
