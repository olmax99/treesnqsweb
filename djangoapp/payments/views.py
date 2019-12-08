from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views import View

from payments.forms import CheckoutForm
from payments.models import NewProject, OrderItem, Order, BillingAddress, Payment

import logging

import stripe
from stripe import error

logger = logging.getLogger(__name__)


def log_error(err):
    return logger.error(f"Status is: {err.http_status},"
                        f"Type is: {err.error.type},"
                        f"Code is: {err.error.code}",
                        f"Param is: {err.error.param}")


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        return render(self.request, "payments/payment.html")

    # TODO: Replace with dj-stripe models if possible
    # Requests are handled to go to https://js.stripe.com/v3/
    # noinspection PyBroadException
    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)
        try:
            # Use Stripe's library to make requests...
            # STEP 1: Create the Charge
            charge = stripe.Charge.create(
                amount=amount,
                currency="chf",
                source=token,
                description="Charge from djangoapp@treesnqs.com"
            )
            # TODO: Can this model be replaced by dj-stripe model? Which one?
            # STEP 2: Create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()
            # STEP 3: Show that order is filled and assign the payment to this order
            order.ordered = True
            order.payment = payment
            order.save()

            # TODO: Implement PaymentIntent API and replace Charge
            # returns client secret, which is used for the entire payment process lifecycle
            # intent = stripe.PaymentIntent.create(
            #     amount=1099,
            #     currency='chf',
            #     payment_method_types=["card"]
            # )

            messages.success(self.request, "Your order was successful.")
            return redirect('treesnqs-home')
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            log_error(err)
            return redirect('treesnqs-home')
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, "Rate error.")
            log_error(err)
            return redirect('treesnqs-home')
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, "Invalid parameters.")
            log_error(err)
            return redirect('treesnqs-home')
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, "Not authenticated.")
            log_error(err)
            return redirect('treesnqs-home')
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, "Network error.")
            log_error(err)
            return redirect('treesnqs-home')
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"Something went wrong. You were not charged. Please try again.")
            log_error(err)
            return redirect('treesnqs-home')
        except Exception as e:
            # Send email to Admin
            messages.error(
                self.request,
                f"Something went wrong. We are notified and do our best to resolve the issue. Please try again later."
            )
            logger.critical(f"{e.__str__()}")
            return redirect('treesnqs-home')


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

