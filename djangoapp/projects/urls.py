from django.urls import path

from projects.views import NewProjectListView, NewProjectDetailView
from . import views

urlpatterns = [
    path('', NewProjectListView.as_view(), name='treesnqs-home'),
    path('projects/<int:pk>/', NewProjectDetailView.as_view(), name='newproject-detail'),
    path('about/', views.about, name='treesnqs-about'),
]
