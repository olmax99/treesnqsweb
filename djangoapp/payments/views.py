from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views import View

from payments.forms import CheckoutForm
from payments.models import NewProject, OrderItem, Order, BillingAddress

import logging

logger = logging.getLogger(__name__)


class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, "payments/payment.html")


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, "payments/checkout-page.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip_code = form.cleaned_data.get('zip_code')
                # TODO: Add save_info functionality
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    countries=country,
                    zip_code=zip_code
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                # logger.info(form.cleaned_data)
                # logger.info("The form is valid.")
                # TODO: Add redirect to the selected payment option
                return redirect('order:checkout')
            messages.warning(self.request, "Failed Checkout.")
            return render(self.request, 'payments/order-summary.html')
        except ObjectDoesNotExist:
            # logger.info(self.request.POST)
            messages.error(self.request, "You don't have any Orders, yet.")
            return redirect('treesnqs-home')


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
            return redirect('treesnqs-home')

