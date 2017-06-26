from __future__ import unicode_literals

from django.db import models

class SystemClientConfig(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return '{} | {}'.format(self.id, self.key)

