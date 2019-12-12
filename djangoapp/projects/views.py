import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from djstripe.models import Customer

from payments.models import OrderItem, Order
from projects.models import NewProject


logger = logging.getLogger(__name__)


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
    customer_qs = Customer.objects.filter(subscriber=request.user)
    # logger.info(f"['treesnqs-home'.'add-to-cart'] {customer_qs[0]}")
    order_query_set = Order.objects.filter(customer=customer_qs[0], ordered=False)
    if order_query_set.exists():
        order = order_query_set[0]
        # check if order_item is already in the order
        if order.items.filter(item__id=project.id).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "The quantity was updated.")
            return redirect('order:order-summary')
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect('order:order-summary')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(customer=customer_qs[0], ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect('order:order-summary')


@login_required
def remove_from_cart(request, pk):
    project = get_object_or_404(NewProject, pk=pk)
    customer_query_set = Customer.objects.filter(subscriber=request.user)
    order_query_set = Order.objects.filter(customer=customer_query_set[0], ordered=False)
    if order_query_set.exists():
        order = order_query_set[0]
        # check if order_item is already in the order
        if order.items.filter(item__id=project.id).exists():
            OrderItem.objects.filter(
                item=project,
                user=request.user,
                ordered=False
            )[0].delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect('newproject-detail', pk)
        else:
            messages.info(request, "This item is not in your cart, yet.")
            return redirect('newproject-detail', pk)
    else:
        messages.info(request, "You do not have an order, yet.")
        return redirect('newproject-detail', pk)


@login_required
def remove_single_item_from_cart(request, pk):
    project = get_object_or_404(NewProject, pk=pk)
    customer_query_set = Customer.objects.filter(subscriber=request.user)
    order_query_set = Order.objects.filter(customer=customer_query_set[0], ordered=False)
    if order_query_set.exists():
        order = order_query_set[0]
        # check if order_item is already in the order
        if order.items.filter(item__id=project.id).exists():
            order_item = OrderItem.objects.filter(
                item=project,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                OrderItem.objects.filter(
                    item=project,
                    user=request.user,
                    ordered=False
                )[0].delete()
            messages.info(request, "The item quantity was updated.")
            return redirect('order:order-summary')
        else:
            messages.info(request, "This item is not in your cart, yet.")
            return redirect('newproject-detail', pk)
    else:
        messages.info(request, "You do not have an order, yet.")
        return redirect('newproject-detail', pk)
