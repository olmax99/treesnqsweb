from django.urls import path

from payments.views import CheckoutView, OrderSummaryView, PaymentView, AddCouponView, RequestRefundView, \
    NewPaymentView, RetrievePaymentIntentView

# Needed for include(... namespace=...)
app_name = 'order'

urlpatterns = [
    path('', CheckoutView.as_view(), name='checkout'),
    path('summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('payment/<pay_option>/', PaymentView.as_view(), name='payment'),
    path('payment-new/<pay_option>/', NewPaymentView.as_view(), name='new-payment'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('refund/request/', RequestRefundView.as_view(), name='request-refund'),
    path('create-payment-intent/', RetrievePaymentIntentView.as_view(), name='retrieve-intent')
]
