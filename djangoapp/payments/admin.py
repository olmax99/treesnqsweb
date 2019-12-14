from django.contrib import admin
from djstripe.admin import StripeModelAdmin
from djstripe.models import PaymentIntent

from payments.models import OrderItem, Order, Payment, Coupon, RefundRequest, BillingAddress


def accept_requested_refund(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


accept_requested_refund.short_description = 'Update orders to refund granted'


# Override for additional info on cancelled PaymentIntents
class PaymentIntentAdmin(StripeModelAdmin):
    list_display = (
        "id",
        "customer",
        "amount",
        "currency",
        "description",
        "amount_capturable",
        "amount_received",
        "receipt_email",
        "canceled_at",
        "status"
    )
    search_fields = ("customer__id", "invoice__id")


class OrderAdmin(admin.ModelAdmin):
    def get_customer_id(self, obj):
        return obj.customer.id

    get_customer_id.short_description = 'Customer'
    get_customer_id.admin_order_field = 'customer__id'

    list_display = [
        'get_customer_id',
        'ordered',
        'order_created',
        'ordered_date',
        'received',
        'refund_requested',
        'refund_granted',
        'billing_address',
        'payment',
        'payment_intent',
        'coupon'
    ]
    list_filter = [
        'ordered',
        'order_created',
        'ordered_date',
        'received',
        'refund_requested',
        'refund_granted'
    ]
    list_display_links = [
        'get_customer_id',
        'billing_address',
        'payment',
        'coupon'
    ]
    search_fields = [
        'customer__id',
        'ref_code'
    ]
    actions = [accept_requested_refund]


class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'amount']


class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ['order', 'reason', 'accepted']


class BillingAddressAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'street_address',
                    'apartment_address',
                    'countries',
                    'zip_code']
    list_filter = ['countries']
    search_fields = ['user',
                     'street_address',
                     'apartment_address',
                     'zip_code']


admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(RefundRequest, RefundRequestAdmin)
admin.site.register(BillingAddress, BillingAddressAdmin)

# Override dj-stripe PaymentIntentAdmin
admin.site.unregister(PaymentIntent)
admin.site.register(PaymentIntent, PaymentIntentAdmin)
