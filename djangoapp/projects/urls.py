from django.urls import path

from projects.views import NewProjectListView, NewProjectDetailView
from .views import about, add_to_cart


urlpatterns = [
    path('', NewProjectListView.as_view(), name='treesnqs-home'),
    path('projects/<int:pk>/', NewProjectDetailView.as_view(), name='newproject-detail'),
    path('about/', about, name='treesnqs-about'),
    path('add-to-cart/<int:pk>/', add_to_cart, name='add-to-cart'),
]
