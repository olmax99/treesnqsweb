from django.urls import path

from . import views

# Needed for include(... namespace=...)
app_name = 'order'

urlpatterns = [
    path('', views.projects_checkout, name='checkout')
]
