from django.contrib.auth.models import User
from django.db import models


class Item(models.Model):
    title = models.CharField(max_length=52)
    # TODO: Depending on user profile, "Default", "Member", "NonProfit"
    price = models.FloatField()

    def __str__(self):
        return self.title


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    order_created = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateField
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
