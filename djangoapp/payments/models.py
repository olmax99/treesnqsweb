from django.contrib.auth.models import User
from django.db import models

from projects.models import NewProject


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
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total
