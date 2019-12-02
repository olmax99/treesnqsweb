from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from projects.models import NewProject


def home(request):
    context = {
        'newproject': NewProject.objects.all()
    }
    return render(request, 'projects/home.html', context)


class NewProjectListView(ListView):
    model = NewProject
    template_name = 'projects/home.html'
    context_object_name = 'newproject'
    ordering = ['-date_posted']


class NewProjectDetailView(LoginRequiredMixin, DetailView):
    model = NewProject


def about(request):
    return render(request, 'projects/about.html', {'title': 'About'})
