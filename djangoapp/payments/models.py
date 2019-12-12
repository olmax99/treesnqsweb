from django.contrib.auth.models import User
from django.db import models
from django_countries.fields import CountryField

from djstripe.models import Charge, Customer, PaymentIntent
from projects.models import NewProject


# TODO: EVALUATE WHICH PARTS OF THE PAYMENTS MODELS CAN BE REPLACED BY DJ-STRIPE MODELS
#  See path/to/side-packages/djstripe/models


# TODO: Evaluate if djstripe.models.core.PaymentIntent can replace this
# This class is used in order to track the lifecycle of the payment
class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=52)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


# THIS IS PART OF THE CORE ORDER MODEL, AND NOT BE REPLACED
class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(NewProject, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.item.price * self.quantity

    def get_total_nonprofit_discount_item_price(self):
        return self.item.discount_price_nonprofit * self.quantity

    def get_total_member_discount_item_price(self):
        return self.item.discount_price_member * self.quantity

    def get_amount_saved_member(self):
        return self.get_total_item_price() - self.get_total_member_discount_item_price()

    def get_amount_saved_nonprofit(self):
        return self.get_total_item_price() - self.get_total_nonprofit_discount_item_price()

    def get_final_price(self):
        if self.user.profile.member and \
                self.item.discount_price_member and \
                self.user.profile.tree == 'member':
            return self.get_total_member_discount_item_price()
        elif self.user.profile.nonprofit and \
                self.item.discount_price_nonprofit and \
                self.user.profile.tree == 'nonprofit':
            return self.get_total_nonprofit_discount_item_price()
        else:
            return self.get_total_item_price()


# THIS IS THE CORE MODEL, WHICH WILL LINK TO ALL DJSTRIPE MODELS
class Order(models.Model):
    # TODO: 2. Next to Stripe indicate the Payment Method and create the
    #  dj-stripe model object accordingly
    #  3. Charge needs to be replaced by PaymentIntent
    """
    Current lifecycle of the Order
    1. Item added to cart
    2. Adding a billing address / indicate the payment method / redeem coupon
    3. Payment via Charge
    4. Received (e.g. Ticket for Project)
    5. Refunds

    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    # ref_code will be replaced by session.client_reference_id
    ref_code = models.CharField(max_length=24)
    items = models.ManyToManyField(OrderItem)
    order_created = models.DateTimeField(auto_now_add=True)
    # TODO: Ordered_date should be set to day when ordered is set to True
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.CASCADE, blank=True, null=True)
    payment_intent = models.ForeignKey(PaymentIntent, on_delete=models.CASCADE, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.CASCADE, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return f"Order by {self.customer.id}"

    def get_total(self):
        # lazy total calculation
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total


# TODO: Verify if can be replaced by path/to/site-packages/djstripe/models/core.Customer
class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=64)
    apartment_address = models.CharField(max_length=64)
    countries = CountryField(multiple=False)
    zip_code = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


# TODO: Replace this model with path/to/site-packages/djstripe/models/billing.Coupon
#  NOTE: Review if djstripe coupons are linked to invoices, if so implement accordingly
class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class RefundRequest(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    refund_email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


