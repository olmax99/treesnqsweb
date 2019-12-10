from django.urls import path

from payments.views import CheckoutView, OrderSummaryView, PaymentView, AddCouponView

# Needed for include(... namespace=...)
app_name = 'order'

urlpatterns = [
    path('', CheckoutView.as_view(), name='checkout'),
    path('summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('payment/<pay_option>/', PaymentView.as_view(), name='payment'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
]
