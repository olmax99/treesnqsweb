from django import template
from django.core.exceptions import ObjectDoesNotExist
from djstripe.models import Customer

from payments.models import Order

register = template.Library()


@register.filter
def cart_item_count(user):
    # if user.is_authenticated:
    #     total = 0
    #     try:
    #         order_items = OrderItem.objects.filter(user=user, ordered=False)
    #         count = order_items.values('quantity')
    #         for i in count:
    #             total += i['quantity']
    #         return total
    #     except ObjectDoesNotExist:
    #         return 0
    if user.is_authenticated:
        customer_qs = Customer.objects.filter(subscriber=user)
        order_qs = Order.objects.filter(customer=customer_qs[0], ordered=False)
        if order_qs.exists():
            return order_qs[0].items.count()
    return 0
