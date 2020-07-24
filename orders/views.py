from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User
from .models import Menu, Cart, Order, Store
from django.http import JsonResponse
import string
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
import stripe

multiple_sizes = {"Regular Pizza":True, "Sicilian Pizza":True, "Dinner Platter":True, "Salad":False, "Sub":True, "Pasta":False}

def index(request):
    return render(request, "orders/index.html")

def menu(request, product):
    product = string.capwords(product.replace('-', ' '))
    items = Menu.objects.filter(type=product)
    if product == "Regular Pizza" or product == "Sicilian Pizza":
        topping = Menu.objects.filter(type="Topping")
        toppings = [(topping[i], topping[i+1], topping[i+2]) for i in range(0, len(topping)-1, 3)]
    else:
        toppings = None
    ## size is used to display different tables in index.html
    size = multiple_sizes[product]
    return render(request, "orders/menu.html", context={"items":items,
                                                        "size":size,
                                                        "product":product,
                                                        "toppings":toppings})

def addToCart(request):
    if request.method == "POST":
        id = request.POST["id"]
        menu_item = Menu.objects.get(id=id)
        user = User.objects.get(id=request.user.id)
        ## If a topping is added, add the topping to cart and remove 1 allowed topping
        if request.POST["name"] == "topping":
            if not Store.objects.filter(type=menu_item.type, name=menu_item.name).exists():
                create = Store(type=menu_item.type, name=menu_item.name)
                create.save()
            ## item (the topping) that will be added to cart
            item = Store.objects.get(type=menu_item.type, name=menu_item.name)
            ## update the allowed number of toppings
            allowed = Cart.objects.filter(customer=user).exclude(topping_allow=0)[0]
            print(allowed.topping_allow)
            allowed.topping_allow -= 1
            allowed_toppings = allowed.topping_allow
            allowed.save()
        else:
            size = request.POST["name"]
            ## Create a new object where the Cart and Order models can refer to
            if not Store.objects.filter(type=menu_item.type, name=menu_item.name, size=size).exists():
                if size == "small":
                    price = menu_item.price_small
                elif size == "large":
                    price = menu_item.price_large
                else:
                    price = menu_item.price_one
                create = Store(type=menu_item.type, name=menu_item.name, size=size, price=price)
                create.save()
            allowed_toppings = menu_item.topping_allow
            item = Store.objects.get(type=menu_item.type, name=menu_item.name, size=size)
        order = Cart(customer=user, item=item, topping_allow=allowed_toppings)
        order.save()
        return JsonResponse({"toppings":allowed_toppings})

def cart(request):
    if request.method == "GET":
        no_ord, ordered, total_price = helper_func(request)
        return render(request, "orders/cart.html", context={"empty":no_ord, "ordered":ordered, "total_price":total_price})
    else:
        remove_items(request)
        return JsonResponse({"success":True})

def confirm(request):
    if request.method == "GET":
        _, ordered, total_price = helper_func(request)
        return render(request, "orders/confirm.html", context={"ordered":ordered, "total_price":total_price})
    else:
        return render(request, "orders/payment.html")

def helper_func(request):
    ordered = [ ]
    tot_price = 0
    orders = Cart.objects.filter(customer=request.user.id)
    for order in orders:
        if order.item.price != None:
            tot_price += order.item.price
        ordered.append((order.id, order.item)) ## REMOVE order.id if necessary
    tot_price = round(tot_price, 2)
    if len(ordered) == 0:
        no_ord = True
    else:
        no_ord = False
    return no_ord, ordered, tot_price

def remove_items(request):
    ids = [int(request.POST["id"])]
    item = Cart.objects.get(id=request.POST["id"])
    if item.item.name == "1 topping":
        ids.append(ids[0] + 1)
    elif item.item.name == "2 toppings":
        ids.append(ids[0] + 1)
        ids.append(ids[0] + 2)
    elif item.item.name == "3 toppings":
        ids.append(ids[0] + 1)
        ids.append(ids[0] + 2)
        ids.append(ids[0] + 3)
    for id in ids:
        Cart.objects.get(id=id).delete()
    return None

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        pass1 = request.POST.get("password1")
        pass2 = request.POST.get("password2")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        ## Make sure all fields were filled
        for i in [username, email, pass1, pass2, first_name, last_name]:
            print(i)
            print(type(i))
            if len(i) == 0:
                return render(request, "orders/register.html", {"field_empty":True})
        ## Check that passwords match and that the email or username is not yet registered
        if pass1 != pass2:
            return render(request, "orders/register.html", {"pass_repeat":True})
        elif User.objects.filter(username=username).exists():
            return render(request, "orders/register.html", {"username_taken":True})
        elif User.objects.filter(email=email).exists():
            return render(request, "orders/register.html", {"email_taken":True})
        else:
            user = User.objects.create_user(username=username, email=email, password=pass1)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            return redirect("login")
    else:
        return render(request, "orders/register.html")

def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        print(username, password)
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            return render(request, "orders/login.html", {"message":"Username and password did not match."})
    else:
        return render(request, "orders/login.html")

def logout_user(request):
    logout(request)
    return redirect("login")

## Page that displays all orders, available only to superusers
@user_passes_test(lambda u: u.is_superuser)
def admin_orders(request):
    orders = Order.objects.all()
    return render(request, "orders/admin_orders.html", context={"orders":orders})

## Payment with stripe
stripe.api_key = settings.STRIPE_SECRET

def payment(request):
    if request.method == "POST":
        try:
            token = request.POST['stripeToken']
            _, _, total_price = helper_func(request)
            ## Convert to cents
            total_price = int(int(total_price)*100 + float(str(total_price)[-2:]))
            customer = stripe.Charge.create(amount=total_price,
                                            currency="USD",
                                            description="Example Charge",
                                            source=token)
            user_obj = User.objects.get(id=request.user.id)
            ## can I just use user.id ???
            orders = Cart.objects.filter(customer=user_obj)
            ## Need to add order number, do I need order_number ???
            ord_count = Order.objects.last().order_number + 1
            for order in orders:
                placed = Order(customer=user_obj, item=order.item, order_number=ord_count)
                placed.save()
            Cart.objects.filter(customer=user_obj).delete()
            return render(request, "orders/order_placed.html", context={"error":"There was an error processing the card."})
        except:
            return False
    else:
        return render(request, "orders/payment.html")
