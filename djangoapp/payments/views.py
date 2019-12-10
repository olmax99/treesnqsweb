from django.http import response
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views import View
# from djstripe.models import Charge

from payments.forms import CheckoutForm, CouponForm
from payments.models import NewProject, OrderItem, Order, BillingAddress, Payment, Coupon

import logging

# import djstripe
# from djstripe import webhooks

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
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            return render(self.request, "payments/payment.html", context)
        else:
            messages.warning(self.request, "A billing address is required.")
            return redirect("order:checkout")

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
            # STEP 2: Create the payment model for handling payment lifecycle later on
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()
            # STEP 3: Assign the payment to this order
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()
            # STEP 4: Show that order is filled
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
            messages.warning(self.request, f"{err.get('message')}")
            log_error(err)
            return redirect('treesnqs-home')
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, "Rate error.")
            log_error(err)
            return redirect('treesnqs-home')
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, "Invalid parameters.")
            log_error(err)
            return redirect('treesnqs-home')
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, "Not authenticated.")
            log_error(err)
            return redirect('treesnqs-home')
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, "Network error.")
            log_error(err)
            return redirect('treesnqs-home')
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"Something went wrong. You were not charged. Please try again.")
            log_error(err)
            return redirect('treesnqs-home')
        except Exception as e:
            # Send email to Admin
            messages.warning(
                self.request,
                f"Something went wrong. We are notified and do our best to resolve the issue. Please try again later."
            )
            logger.critical(f"{e.__str__()}")
            return redirect('treesnqs-home')


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, "payments/checkout-page.html", context)
        except ObjectDoesNotExist:
            return redirect("order:checkout")

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
                if payment_option == 'S':
                    return redirect('order:payment', pay_option='stripe')
                # elif payment_option == 'P':
                #     return redirect('order:payment', pay_option='paypal')
                else:
                    messages.warning(self.request, "Invalid payment option.")
                    return render(self.request, 'payments/order-summary.html')
        except ObjectDoesNotExist:
            # logger.info(self.request.POST)
            messages.warning(self.request, "You don't have any Orders, yet.")
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
            messages.warning(self.request, "You don't have any Orders, yet.")
            return redirect('treesnqs-home')


@login_required
def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist.")
        return redirect("order:checkout")


class AddCouponView(LoginRequiredMixin,View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user, ordered=False)
                res = get_coupon(self.request, code)
                if type(res) is response.HttpResponseRedirect:
                    return res
                order.coupon = res
                order.save()
                messages.success(self.request, "Your coupon was successfully redeemed.")
                return redirect("order:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order.")
                return redirect("order:checkout")


