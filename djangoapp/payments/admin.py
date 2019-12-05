from django.contrib import admin

from payments.models import OrderItem, Order


admin.site.register(OrderItem)
admin.site.register(Order)
