from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("menu/<product>/", views.menu, name="menu"),
    path("register", views.register, name="register"),
    path("add_to_cart", views.addToCart, name="add_to_cart"),
    path("cart", views.cart, name="cart"),
    path("confirm", views.confirm, name="confirm"),
    path("login/", views.login_user, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("payment", views.payment, name="payment"),
    path("admin_orders", views.admin_orders, name="admin_orders")
]
