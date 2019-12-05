from django.contrib.auth.models import User
from django.db import models

from projects.models import NewProject


# class Item(models.Model):
#     title = models.CharField(max_length=52)
#     # TODO: Depending on user profile, "Default", "Member", "NonProfit"
#     price = models.FloatField()
#
#     def __str__(self):
#         return self.title


class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(NewProject, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    order_created = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateField
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
