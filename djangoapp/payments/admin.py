from django.contrib import admin

from payments.models import Item, OrderItem, Order


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
