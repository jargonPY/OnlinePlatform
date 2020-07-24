from django.db import models
from django.conf import settings

class Menu(models.Model):
    type = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    topping_allow = models.IntegerField(default=0)
    price_small = models.FloatField(blank=True, null=True)
    price_large = models.FloatField(blank=True, null=True)
    price_one = models.FloatField(blank=True, null=True)

class Store(models.Model):
    type =  models.CharField(max_length=30)
    name =  models.CharField(max_length=30)
    size =  models.CharField(max_length=20, blank=True)
    price =  models.FloatField(blank=True, null=True)

class Cart(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True)
    topping_allow = models.IntegerField(default=0)

class Order(models.Model):
    """ Before orders are deleted from the cart, move them here so they are stored as orders, and the cart can be empty """
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True)
    order_number = models.IntegerField()
    date_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer id:{self.customer}, Item id:{self.item}, Order number:{self.order_number} Date added:{self.date_added}"
