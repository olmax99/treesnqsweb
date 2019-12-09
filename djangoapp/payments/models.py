from django.contrib.auth.models import User
from django.db import models
from django_countries.fields import CountryField

from djstripe.models import Charge
from projects.models import NewProject


# TODO: EVALUATE WHICH PARTS OF THE PAYMENTS MODELS CAN BE REPLACED BY DJ-STRIPE MODELS
#  See path/to/side-packages/djstripe/models


# TODO: Evaluate if djstripe.models.core.Charge can replace this:
# This class is used in order to track the lifecycle of the payment
class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=52)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


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


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    order_created = models.DateTimeField(auto_now_add=True)
    # TODO: Ordered_date should be set to day when ordered is set to True
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.CASCADE, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.CASCADE, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


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

    def __str__(self):
        return self.code


