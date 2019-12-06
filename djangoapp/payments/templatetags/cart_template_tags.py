from django import template
from django.core.exceptions import ObjectDoesNotExist

from payments.models import OrderItem

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        total = 0
        try:
            order = OrderItem.objects.filter(user=user, ordered=False)
            count = order.values('quantity')
            for i in count:
                total += i['quantity']
            return total
        except ObjectDoesNotExist:
            return 0
