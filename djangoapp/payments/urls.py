from django.urls import path

from payments.views import CheckoutView, OrderSummaryView, AddCouponView, RequestRefundView, \
    PaymentView, RetrievePaymentIntentView

# Needed for include(... namespace=...)
app_name = 'order'

urlpatterns = [
    path('', CheckoutView.as_view(), name='checkout'),
    path('summary/', OrderSummaryView.as_view(), name='order-summary'),
    # path('payment-old/<pay_option>/', PaymentView.as_view(), name='payment-old'),
    path('payment/<pay_option>/', PaymentView.as_view(), name='payment'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('refund/request/', RequestRefundView.as_view(), name='request-refund'),
    path('create-payment-intent/', RetrievePaymentIntentView.as_view(), name='get-payment-intent')
]
