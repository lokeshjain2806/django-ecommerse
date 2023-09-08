from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views import View
from .models import *
from .forms import CustumerRegistrationForm, CustumerProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class ProductView(View):
    def get(self, request):
        laptop = Product.objects.filter(category='L')
        mobile = Product.objects.filter(category='M')
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        context = {
            'laptop': laptop,
            'mobile': mobile,
            'topwears': topwears,
            'bottomwears': bottomwears
        }
        return render(request, 'app/home.html',context)


class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        return render(request, 'app/productdetail.html', {'product':product, 'item_already_in_cart': item_already_in_cart})


@login_required(login_url="/account/login/")
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart/')


@login_required(login_url="/account/login/")
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user = request.user)
        amount = 0.0
        shipping_amount = 0.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discount_price)
                amount += tempamount
                total_amount = amount+ shipping_amount
            return render(request, 'app/addtocart.html', {'carts': cart, 'total_amount': total_amount, 'amount': amount, 'shipping_amount': shipping_amount})
        else:
            return render(request,'app/emptycart.html')


@login_required(login_url="/account/login/")
def plus_cart(request):
    if request.method == 'GET':
        user = request.user
        prod_id = request.GET['prod_id']
        c = Cart.objects.filter(product=prod_id, user=user).first()
        c.quantity += 1
        c.save()
        amount = 0.0
        shipping_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discount_price)
            amount += tempamount
            total_amount = amount + shipping_amount
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'total_amount': total_amount
            }
        return JsonResponse(data)


@login_required(login_url="/account/login/")
def minus_cart(request):
    if request.method == 'GET':
        user = request.user
        prod_id = request.GET['prod_id']
        c = Cart.objects.filter(product=prod_id, user=user).first()
        c.quantity -= 1
        c.save()
        amount = 0.0
        shipping_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]

        for item in cart_product:
            if item.quantity == 0:
                c.delete()
                return render(request, 'app/emptycart.html')

        for p in cart_product:
            tempamount = (p.quantity * p.product.discount_price)
            amount += tempamount
            total_amount = amount + shipping_amount
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'total_amount': total_amount
            }
        return JsonResponse(data)


@login_required(login_url="/account/login/")
def remove_cart(request):
    if request.method == 'GET':
        user = request.user
        prod_id = request.GET['prod_id']
        c = Cart.objects.filter(product=prod_id, user=user).first()
        c.delete()
        amount = 0.0
        shipping_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discount_price)
            amount += tempamount
        data = {
            'amount': amount,
            'total_amount': amount + shipping_amount
            }
        return JsonResponse(data)


@method_decorator(login_required(login_url="/account/login/"), name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustumerProfileForm
        return render(request, 'app/profile.html', {'form': form , 'active': 'btn-primary'})

    def post(self, request):
        usr = request.user
        form = CustumerProfileForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            pincode = form.cleaned_data['pincode']
            reg = Custumer(user=usr, name=name, locality=locality, city=city, state=state, pincode=pincode)
            reg.save()
            messages.success(request, 'Congratulation!! Profile Updated Sucessfully')
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})


@login_required(login_url="/account/login/")
def address(request):
    add = Custumer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add': add, 'active': 'btn-primary'})


@login_required(login_url="/account/login/")
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'order_placed': op})


def mobile(request, data=None):
    if data is None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'vivo':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'nokia':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'realme':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'poco':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'iqoo':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'below':
        mobiles = Product.objects.filter(category='M', discount_price__lt=10000)
    elif data == 'above':
        mobiles = Product.objects.filter(category='M', discount_price__gt=10000)
    return render(request, 'app/mobile.html', {'mobiles': mobiles})


def laptop(request, data=None):
    if data is None:
        laptops = Product.objects.filter(category='L')
    elif data == 'microsoft':
        laptops = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'dell':
        laptops = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'hp':
        laptops = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'lenovo':
        laptops = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'apple':
        laptops = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'below':
        laptops = Product.objects.filter(category='L', discount_price__lt=100000)
    elif data == 'above':
        laptops = Product.objects.filter(category='L', discount_price__gt=100000)
    return render(request, 'app/laptop.html', {'laptops': laptops})


def top_wear(request, data=None):
    if data is None:
        top_wears = Product.objects.filter(category='TW')
    elif data == 'jbfashion':
        top_wears = Product.objects.filter(category='TW').filter(brand=data)
    elif data == 'vcom':
        top_wears = Product.objects.filter(category='TW').filter(brand=data)
    elif data == 'wardrobe':
        top_wears = Product.objects.filter(category='TW').filter(brand=data)
    elif data == 'ethnic':
        top_wears = Product.objects.filter(category='TW').filter(brand=data)
    elif data == 'readymade':
        top_wears = Product.objects.filter(category='TW').filter(brand=data)
    elif data == 'warm':
        top_wears = Product.objects.filter(category='TW').filter(brand=data)
    return render(request, 'app/top_wear.html', {'top_wears': top_wears})


def bottom_wear(request, data=None):
    if data is None:
        bottom_wears = Product.objects.filter(category='BW')
    elif data == 'fabulous':
        bottom_wears = Product.objects.filter(category='BW').filter(brand=data)
    elif data == 'lycra':
        bottom_wears = Product.objects.filter(category='BW').filter(brand=data)
    elif data == 'xxllent':
        bottom_wears = Product.objects.filter(category='BW').filter(brand=data)
    elif data == 'fabrics':
        bottom_wears = Product.objects.filter(category='BW').filter(brand=data)
    elif data == 'johnpride':
        bottom_wears = Product.objects.filter(category='BW').filter(brand=data)
    elif data == 'fronttrousers':
        bottom_wears = Product.objects.filter(category='BW').filter(brand=data)
    return render(request, 'app/bottom_wear.html', {'bottom_wears': bottom_wears})


class CustumerRegistrationView(View):
    def get(self, request):
        form = CustumerRegistrationForm
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustumerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,'Congratulations!! Registered Successfully')
            form.save()
        return render(request, 'app/customerregistration.html', {'form': form})

@login_required(login_url="/account/login/")
def checkout(request):
    user = request.user
    add = Custumer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    totalamount = 0.0
    shipping_amount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discount_price)
            amount += tempamount
        totalamount = amount + shipping_amount
    return render(request, 'app/checkout.html', {'add': add, 'totalamount': totalamount , 'cart_items': cart_items})


@login_required(login_url="/account/login/")
def paymentdone(request):
    user = request.user
    custid = request.GET.get('custid')
    custumer = Custumer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user= user, custumer= custumer, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect("orders")