from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.checks import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views import View

from payments.models import NewProject, OrderItem, Order


@login_required
def projects_checkout(request):
    context = {
        'newproject': NewProject.objects.all()
    }
    return render(request, "payments/checkout-page.html", context)


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'payments/order-summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have any Orders, yet.")
            return redirect('/')
