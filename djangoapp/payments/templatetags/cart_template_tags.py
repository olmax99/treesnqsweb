from django import template
from django.core.exceptions import ObjectDoesNotExist

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
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].items.count()
    return 0
