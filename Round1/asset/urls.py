from django.conf.urls import url
from django.contrib import admin
from .views import *


urlpatterns = [
    url(r'^get/all/stock/items/$', get_all_stock_items),
    url(r'^get/stock/items/for/sale/$', get_stock_items_for_sale),
    url(r'^save/stock/item/$', save_stock_item),
    url(r'^save/sale/order/$', save_sale_order),
    url(r'^save/stock/transfer/request/$', save_stock_transfer_request),
    url(r'^get/all/stock_transfer_requests/$', get_all_stock_transfer_requests),
    url(r'^get/stock_transfer_request/$', get_stock_transfer_request),
    url(r'^save/purchase_order/$', save_purchase_order),
    url(r'^get/all/purchase_orders/$', get_all_purchase_orders),
    url(r'^get/purchase_order/$', get_purchase_order),
    url(r'^mark/purchase/order/completed/$', mark_purchase_order_completed),
    url(r'^save/recipe/$', save_recipe),
    url(r'^produce/finished/items/$', produce_finished_items),
    url(r'^manaul/stock/verification/$', manual_stock_verification),
    
    url(r'^get/active/recipe/(?P<id>\d+)/$', current_recipe),


]
