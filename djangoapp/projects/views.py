from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from payments.models import OrderItem, Order
from projects.models import NewProject


class NewProjectListView(ListView):
    model = NewProject
    template_name = 'projects/home.html'
    context_object_name = 'newproject'
    ordering = ['-date_posted']


class NewProjectDetailView(LoginRequiredMixin, DetailView):
    model = NewProject
    context_object_name = 'newproject'


def about(request):
    return render(request, 'projects/about.html', {'title': 'About'})


@login_required
def add_to_cart(request, pk):
    project = get_object_or_404(NewProject, pk=pk)
    order_item, created = OrderItem.objects.get_or_create(
        item=project,
        user=request.user,
        ordered=False
    )
    order_query_set = Order.objects.filter(user=request.user, ordered=False)
    if order_query_set.exists():
        order = order_query_set[0]
        # check if order_item is already in the order
        if order.items.filter(item__id=project.id).exists():
            order_item.quantity += 1
            order_item.save()
        else:
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user)
        order.items.add(order_item)
    return redirect('newproject-detail', pk)
