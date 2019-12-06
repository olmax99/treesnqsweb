from django.urls import path

from payments.views import projects_checkout, OrderSummaryView

# Needed for include(... namespace=...)
app_name = 'order'

urlpatterns = [
    path('', projects_checkout, name='checkout'),
    path('summary/', OrderSummaryView.as_view(), name='order-summary')
]
