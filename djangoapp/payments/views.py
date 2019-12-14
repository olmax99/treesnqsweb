import json
import random
import string

from django.contrib.auth.models import User
from django.core import serializers
from django.db.models.signals import post_save
from django.http import response, HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from djstripe import webhooks
from djstripe.models import Customer, PaymentIntent
from djstripe.sync import sync_subscriber

from payments.forms import CheckoutForm, CouponForm, RefundForm
from payments.models import Order, BillingAddress, Payment, Coupon, RefundRequest


import logging

# import djstripe
# from djstripe import webhooks

import stripe
from stripe import error

"""
See all stripe webhook event types 
https://stripe.com/docs/api/events/types

"""

logger = logging.getLogger(__name__)


# TODO: Verify how this process can be integrated into path/to/site-packages/djstripe/models/checkout.Session
"""
STRIPE: We recommend creating a PaymentIntent as soon as the amount is known, 
        such as when the customer begins the checkout process.
        
        DO NOT USE STRIPE.JS CHECKOUT - the credit card form will do, bc PaymentIntents
        are set up already

CURRENT CHECKOUT LIFECYCLE (NEW: DJSTRIPE):

0. User is registered and logged in
   NEW:
     - create Customer (Django Signals)
1. User fills his cart in OrderSummaryView -> proceeds to checkout
   NEW:
     - create PaymentIntent
     - create new session ???
2. In CheckoutView user provides address and payment provider. He can optionally redeem a coupon -> proceeds to payment
3. User provides credit card credentials -> submit transaction
   NEW:
     - fetch PaymentIntent from 
4. Option for refund

"""


def log_error(err):
    return logger.error(f"Status is: {err.http_status},"
                        f"Type is: {err.error.type},"
                        f"Code is: {err.error.code}",
                        f"Param is: {err.error.param}")


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


@webhooks.handler("payment_intent")
def payment_intent_hook(event, **kwargs):
    # logger.info(f"[dj-stripe: hook]: PaymentIntent - {event.type}")
    if event.type == 'payment_intent.created':
        logger.info(f"[dj-stripe: hook]: {event.type} - create")

    elif event.type == 'payment_intent.succeeded':
        logger.info(f"[dj-stripe: hook]: {event.type} - success")
        # logger.info(f"[dj-stripe: hook]: {event.data}")
        # try:
        #     customer = event.data.customer
        #     order = Order.objects.get(customer=customer, ordered=False)
        #     # STEP 3: Assign the payment to this order
        #     order_items = order.items.all()
        #     order_items.update(ordered=True)
        #     for item in order_items:
        #         item.save()
        #     # STEP 4: Show that order is filled
        #     order.ordered = True
        #     # order.payment = payment
        #     order.ref_code = order_reference()
        #     order.save()
        # except AttributeError as e:
        #     messages.warning(self.request, "There are no OrderItems associated with this checkout.")
        #     return redirect('treesnqs-home')
        return redirect('order:payment-intent-succeeded')

    elif event.type == 'payment_intent.payment_failed':
        logger.info(f"[dj-stripe: hook]: {event.type} - failed")

    # payment_intent.amount_capturable_updated
    else:
        logger.info(f"[dj-stripe: hook]: {event.type} - updated")


# --------------- User Creation Signal for Customer object creation-----------------

# Every new user profile triggers the related customer object creation
def customer_receiver(sender, instance, created, *args, **kwargs):
    if created:
        customer = sync_subscriber(subscriber=instance)
        logger.info(f"[dj-stripe]: Customer created locally - {customer}")


# Utilize post_save signal when User is created
post_save.connect(customer_receiver, sender=User)

# ---------------------------------------------------------------------------------


def order_reference():
    return '-'.join([''.join(
        random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(4)])


@csrf_exempt
def payment_intent_succeeded_view(request):
    # payload = request.body
    # event = None
    #
    # try:
    #     event = stripe.Event.construct_from(
    #       json.loads(payload), stripe.api_key
    #     )
    # except ValueError as e:
    #     # Invalid payload
    #     return HttpResponse(status=400)
    #
    # # Handle the event
    # if event.type == 'payment_intent.succeeded':
    #     payment_intent = event.data.object # contains a stripe.PaymentIntent
    #     handle_payment_intent_succeeded(payment_intent)
    #     elif event.type == 'payment_method.attached':
    #     payment_method = event.data.object # contains a stripe.PaymentMethod
    #     handle_payment_method_attached(payment_method)
    #     # ... handle other event types
    # else:
    #     # Unexpected event type
    #     return HttpResponse(status=400)
    logging.info(f"GOT IT.")
    return HttpResponse(status=200)


class RetrievePaymentIntentView(View):
    def post(self, *args, **kwargs):
        try:
            # Retrieve active payment intent
            customer_qs = Customer.objects.filter(subscriber=self.request.user)
            payment_intent_qs = PaymentIntent.objects.filter(customer=customer_qs[0]).exclude(
                status='succeeded').exclude(status='canceled')
            payment_intent = payment_intent_qs.get(customer=customer_qs[0])
            # EXPECTED OUTPUT
            out = {
                "clientSecret": payment_intent.client_secret,
                "publishableKey": settings.STRIPE_TEST_PUBLIC_KEY
            }
            # logging.info(f"[RetrievePaymentIntent] JSON output: {out}")
            return JsonResponse(out)
        except ObjectDoesNotExist:
            # logger.info(self.request.POST)
            messages.warning(self.request, "There are no OrderItems associated with this checkout.")
            return redirect('treesnqs-home')


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        customer_qs = Customer.objects.filter(subscriber=self.request.user)
        # payment_intent = PaymentIntent.objects.get(customer=customer_qs[0])
        order = Order.objects.get(customer=customer_qs[0], ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            return render(self.request, "payments/payment.html", context)
        else:
            messages.warning(self.request, "A billing address is required.")
            return redirect("order:checkout")


# class PaymentView(LoginRequiredMixin, View):
#     def get(self, *args, **kwargs):
#         customer_qs = Customer.objects.filter(subscriber=self.request.user)
#         order = Order.objects.get(customer=customer_qs[0], ordered=False)
#         if order.billing_address:
#             context = {
#                 'order': order,
#                 'DISPLAY_COUPON_FORM': False
#             }
#             return render(self.request, "payments/payment.html", context)
#         else:
#             messages.warning(self.request, "A billing address is required.")
#             return redirect("order:checkout")
#
#     # TODO: Replace with dj-stripe models if possible
#     # Requests are handled to go to https://js.stripe.com/v3/
#     # noinspection PyBroadException
#     def post(self, *args, **kwargs):
#         customer_qs = Customer.objects.filter(subscriber=self.request.user)
#         order = Order.objects.get(customer=customer_qs[0], ordered=False)
#         # TODO: What is the relationship between subscriber and User?
#         # customer_profile = Customer.objects.get(subsciber=)
#
#         # Token used to be for one-time payments, which are not working with PaymentIntents
#         # CUSTOMER OBJECT ALWAYS REQUIRED
#         token = self.request.POST.get('stripeToken')
#
#         # ----------------- Legacy Stripe Charge API-----------------------------------
#
#         amount = int(order.get_total() * 100)
#         try:
#             # Use Stripe's library to make requests...
#             # STEP 1: Create the Charge
#             charge = stripe.Charge.create(
#                 amount=amount,
#                 currency="chf",
#                 source=token,
#                 description="Charge from djangoapp@treesnqs.com"
#             )
#             # TODO: Can this model be replaced by dj-stripe model? Which one?
#             # STEP 2: Create the payment model for handling payment lifecycle
#             payment = Payment()
#             payment.stripe_charge_id = charge['id']
#             payment.user = self.request.user
#             payment.amount = order.get_total()
#             payment.save()
#             # STEP 3: Assign the payment to this order
#             order_items = order.items.all()
#             order_items.update(ordered=True)
#             for item in order_items:
#                 item.save()
#             # STEP 4: Show that order is filled
#             order.ordered = True
#             order.payment = payment
#             order.ref_code = order_reference()
#             order.save()
#
#             messages.success(self.request, "Your order was successful.")
#             return redirect('treesnqs-home')
#         except stripe.error.CardError as e:
#             # Since it's a decline, stripe.error.CardError will be caught
#             body = e.json_body
#             err = body.get('error', {})
#             messages.warning(self.request, f"{err.get('message')}")
#             log_error(err)
#             return redirect('treesnqs-home')
#         except stripe.error.RateLimitError as e:
#             # Too many requests made to the API too quickly
#             body = e.json_body
#             err = body.get('error', {})
#             messages.warning(self.request, "Rate error.")
#             log_error(err)
#             return redirect('treesnqs-home')
#         except stripe.error.InvalidRequestError as e:
#             # Invalid parameters were supplied to Stripe's API
#             body = e.json_body
#             err = body.get('error', {})
#             messages.warning(self.request, "Invalid parameters.")
#             log_error(err)
#             return redirect('treesnqs-home')
#         except stripe.error.AuthenticationError as e:
#             # Authentication with Stripe's API failed
#             # (maybe you changed API keys recently)
#             body = e.json_body
#             err = body.get('error', {})
#             messages.warning(self.request, "Not authenticated.")
#             log_error(err)
#             return redirect('treesnqs-home')
#         except stripe.error.APIConnectionError as e:
#             # Network communication with Stripe failed
#             body = e.json_body
#             err = body.get('error', {})
#             messages.warning(self.request, "Network error.")
#             log_error(err)
#             return redirect('treesnqs-home')
#         except stripe.error.StripeError as e:
#             # Display a very generic error to the user, and maybe send
#             # yourself an email
#             body = e.json_body
#             err = body.get('error', {})
#             messages.warning(self.request, f"Something went wrong. You were not charged. Please try again.")
#             log_error(err)
#             return redirect('treesnqs-home')
#         except Exception as e:
#             # Send email to Admin
#             messages.warning(
#                 self.request,
#                 f"Something went wrong. We are notified and do our best to resolve the issue. Please try again later."
#             )
#             logger.critical(f"{e.__str__()}")
#             return redirect('treesnqs-home')


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            customer_qs = Customer.objects.filter(subscriber=self.request.user)
            order = Order.objects.get(customer=customer_qs[0], ordered=False)
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
            customer_qs = Customer.objects.filter(subscriber=self.request.user)
            order = Order.objects.get(customer=customer_qs[0], ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip_code = form.cleaned_data.get('zip_code')
                # TODO: Add save_info functionality
                # save_info = form.cleaned_data.get('save_info')
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
                payment_option = form.cleaned_data.get('payment_option')
                payment_method = form.cleaned_data.get('payment_method')
                if payment_option == 'S' and payment_method == 'card':
                    # if payment_method == 'card':
                    #     payment_method_stripe = stripe.PaymentMethod.create(
                    #         type="card",
                    #         card={"number": "4242424242424242",
                    #               "exp_month": 12,
                    #               "exp_year": 2020,
                    #               "cvc": "314",
                    #               },)
                    #     logger.info(f"[order:checkout] paymentMethod created: {payment_method_stripe}")
                    #     payment_method = PaymentMethod.attach(payment_method_stripe,
                    #                                           customer_qs[0])
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
            customer_qs = Customer.objects.filter(subscriber=self.request.user)
            payment_intent_qs = PaymentIntent.objects.filter(customer=customer_qs[0]).exclude(
                status='canceled').exclude(status='succeeded')
            # logging.info(f"[OrderSummaryView] PaymentIntents QuerySet (Exclude 'succeeded,canceled': {payment_intent_qs}")
            order = Order.objects.get(customer=customer_qs[0], ordered=False)
            # STEP 1: Create new PaymentIntent or update amount of existing
            if payment_intent_qs.exists():
                amount_updated = order.get_total()
                payment_intent = payment_intent_qs.get(customer=customer_qs[0])
                if amount_updated != payment_intent.amount:
                    # logger.info(f"['dj-stripe'] captured payment_intent: {payment_intent}")
                    payment_intent.amount = amount_updated
                    payment_intent.update(sid=payment_intent_qs[0].id,
                                          amount=int(amount_updated*100))
                    payment_intent.save()
            elif not payment_intent_qs.exists() and len(order.items.all()) < 1:
                messages.warning(self.request, "You don't have any Orders, yet.")
                return redirect('treesnqs-home')
            else:
                # hook to Stripe client will trigger sync
                payment_intent_stripe = stripe.PaymentIntent.create(
                    customer=customer_qs[0].id,
                    amount=int(order.get_total()*100),
                    currency="chf")
                PaymentIntent.sync_from_stripe_data(payment_intent_stripe)
                # logger.info(f"['order:order-summary'] NEW PaymentIntent : {payment_intent_stripe.id}")
            # STEP 2: Show Order Summary
            context = {
                'object': order
            }
            return render(self.request, 'payments/order-summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You don't have any Orders, yet.")
            return redirect('treesnqs-home')


class AddCouponView(LoginRequiredMixin, View):
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


class RequestRefundView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "payments/request-refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST or None)
        if form.is_valid():
            try:
                ref_code = form.cleaned_data.get('ref_code')
                message = form.cleaned_data.get('message')
                contact = form.cleaned_data.get('refund_email')
                # Step 1: Edit the order
                try:
                    order = Order.objects.get(ref_code=ref_code)
                    order.refund_requested = True
                    order.save()

                    # Step 2: Store the refund
                    refund = RefundRequest()
                    refund.order = order
                    refund.reason = message
                    refund.refund_email = contact
                    refund.save()
                    messages.success(self.request, "We have received your request for refund.")
                    return redirect("treesnqs-home")
                except ObjectDoesNotExist:
                    messages.info(self.request, "Could't find a matching Order.")
                    return redirect("order:request-refund")
            except ObjectDoesNotExist:
                messages.info(self.request, "Ensure that the input is valid.Please try again.")
                return redirect("order:request-refund")
