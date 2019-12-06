from django.urls import path

from projects.views import (
    NewProjectListView,
    NewProjectDetailView,
    about,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart
)


urlpatterns = [
    path('', NewProjectListView.as_view(), name='treesnqs-home'),
    path('projects/<int:pk>/', NewProjectDetailView.as_view(), name='newproject-detail'),
    path('about/', about, name='treesnqs-about'),
    path('add-to-cart/<int:pk>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<int:pk>/', remove_from_cart, name='remove-from-cart'),
    path('remove-single-item/<int:pk>/', remove_single_item_from_cart, name='remove-single-item'),
]
