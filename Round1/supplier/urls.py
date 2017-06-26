from django.conf.urls import url
from django.contrib import admin
from .views import *


urlpatterns = [
    url(r'^get/all/suppliers/$', get_all_suppliers),
    url(r'^add/supplier/$', add_supplier),
]
