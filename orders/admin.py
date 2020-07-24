from django.contrib import admin
from .models import Menu, Cart, Order, Store

admin.site.register(Menu)
admin.site.register(Store)
admin.site.register(Cart)
admin.site.register(Order)
