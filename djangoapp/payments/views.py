from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from payments.models import NewProject, OrderItem, Order


@login_required
def projects_checkout(request):
    context = {
        'newproject': NewProject.objects.all()
    }
    return render(request, "payments/checkout-page.html", context)


# @login_required
# def add_to_cart(request, pk):
#     project = get_object_or_404(NewProject, pk=pk)
#     order_item = OrderItem.objects.create(item=project)
#     order_query_set = Order.objects.filter(user=request.user, ordered=False)
#     if order_query_set .exists():
#         order = order_query_set[0]
#         # check if order_item is already in the order
#         if order.item.filter(project__pk=project.pk).exists():
#             order_item.quantity += 1
#             order_item.save()
#     else:
#         ordered_date = timezone.now()
#         order = OrderItem.objects.create(user=request.user, ordered_date=ordered_date)
#         order.items.add(order_item)
#     return redirect('projects/newproject-detail', pk)
