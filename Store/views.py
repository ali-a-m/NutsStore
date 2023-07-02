from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from .models import Product, Warehouse, ProductType
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from functools import wraps
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def seller_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_seller():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('store')  # Replace 'home' with your desired page URL name
    return wrapper

from django.db.models import Prefetch

@method_decorator(login_required, name='dispatch')
class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_authenticated and user.is_customer() and user.city:
            queryset = queryset.filter(warehouse__city=user.city)

        # If the user is a seller, filter the queryset to show only their products
        if user.is_authenticated and user.is_seller():
            queryset = queryset.filter(seller=user)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated and user.is_customer() and user.city:
            context['product_types'] = ProductType.objects.filter(product__warehouse__city=user.city).distinct()
        if user.is_authenticated and user.is_seller():
            context['product_types'] = ProductType.objects.distinct()

        return context

@method_decorator(login_required, name='dispatch')
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

@method_decorator([login_required, seller_required], name='dispatch')
class ProductCreateView(CreateView):
    model = Product
    template_name = 'product_create.html'
    fields = ['name', 'description', 'price', 'product_type', 'amount', 'warehouse', 'main_photo'] # additional_photos
    success_url = reverse_lazy('store')

    def form_valid(self, form):
        form.instance.seller = self.request.user  # Set the seller as the current user
        return super().form_valid(form)
    
@method_decorator([login_required, seller_required], name='dispatch')
class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('store')

    def get_queryset(self):
        # Only allow the user who created the product to delete it
        queryset = super().get_queryset()
        queryset = queryset.filter(seller=self.request.user)
        return queryset
    
from django.views.generic import UpdateView
from .forms import ChangePriceForm

@method_decorator([login_required, seller_required], name='dispatch')
class ChangePriceView(UpdateView):
    model = Product
    form_class = ChangePriceForm
    template_name = 'product_detail.html'
    success_url = '/' # URL to redirect after successfully updating the price

    def get_queryset(self):
        # Only allow the user who created the product to delete it
        queryset = super().get_queryset()
        queryset = queryset.filter(seller=self.request.user)
        return queryset

 
# @method_decorator([login_required, seller_required], name='dispatch')
# class WarehouseCreateView(CreateView):
#     model = Warehouse
#     template_name = 'create_warehouse.html'
#     fields = ['name', 'city', 'location']
#     success_url = reverse_lazy('warehouse-list')

#     def form_valid(self, form):
#         form.instance.seller = self.request.user  # Set the seller as the current user
#         return super().form_valid(form)

from .forms import WarehouseCreateForm
from accounts.models import City

@method_decorator([login_required, seller_required], name='dispatch')
class WarehouseCreateView(CreateView):
    model = Warehouse
    template_name = 'create_warehouse.html'
    form_class = WarehouseCreateForm
    success_url = reverse_lazy('warehouse-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['city_queryset'] = City.objects.all()  # Pass the queryset of cities to the form
        return kwargs

    def form_valid(self, form):
        form.instance.seller = self.request.user  # Set the seller as the current user
        return super().form_valid(form)
    
@method_decorator([login_required, seller_required], name='dispatch')
class WarehouseListView(ListView):
    model = Warehouse
    template_name = 'warehouse_list.html'
    context_object_name = 'warehouses'

@method_decorator([login_required, seller_required], name='dispatch')
class WarehouseDetailView(DetailView):
    model = Warehouse
    template_name = 'warehouse_detail.html'
    context_object_name = 'warehouse'

# @method_decorator([login_required, seller_required], name='dispatch')
class WarehouseDeleteView(DeleteView):
    model = Warehouse
    template_name = 'warehouse_confirm_delete.html'
    success_url = reverse_lazy('warehouse-list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.seller != request.user:
            raise PermissionDenied  # Raise an exception if the user is not the seller
        return super().dispatch(request, *args, **kwargs)


from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = request.session.get('cart', {})
    amount = int(request.POST.get('amount', 1))  # Get the specified quantity from the form, defaulting to 1 if not provided

    if str(product_id) in cart:
        # If the product is already in the cart, increment the quantity
        cart[str(product_id)]['quantity'] += amount
    else:
        # If the product is not in the cart, add it with the specified quantity
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': amount
        }

    request.session['cart'] = cart
    return redirect('cart')

def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    item = cart.get(str(item_id))

    if item:
        del cart[str(item_id)]

    request.session['cart'] = cart
    return redirect('cart')

def add_one_cart(request, item_id):
    cart = request.session.get('cart', {})
    item = cart.get(str(item_id))

    if item:
        cart[str(item_id)]['quantity'] += 1

    request.session['cart'] = cart
    return redirect('cart')


def remove_one_cart(request, item_id):
    cart = request.session.get('cart', {})
    item = cart.get(str(item_id))

    if item:
        quantity = item['quantity']

        if quantity > 1:
            cart[str(item_id)]['quantity'] -= 1
        else:
            del cart[str(item_id)]

    request.session['cart'] = cart
    return redirect('cart')

# def update_cart(request, item_id):
#     cart = request.session.get('cart', {})
#     item = cart.get(str(item_id))

#     if item:
#         quantity = int(request.POST.get('quantity', 0))

#         if quantity > 0:
#             item['quantity'] = quantity
#         else:
#             del cart[str(item_id)]

#     request.session['cart'] = cart
#     return redirect('cart')

from decimal import Decimal
from django.shortcuts import render

# def cart_view(request):
#     cart = request.session.get('cart', {})
#     total_price = 0

#     for item in cart.values():
#         quantity = item['quantity']
#         price = item['price']
#         subtotal = price * quantity
#         item['subtotal'] = subtotal
#         total_price += subtotal

#     context = {
#         'cart': cart,
#         'total_price': total_price,
#     }

#     return render(request, 'cart.html', context)

from .models import Order, Cart
from django.db import transaction

def cart_view(request):
    cart = request.session.get('cart', {})
    total_price = 0

    for item in cart.values():
        quantity = item['quantity']
        price = item['price']
        subtotal = price * quantity
        item['subtotal'] = subtotal
        total_price += subtotal

    if request.method == 'POST':
        with transaction.atomic():
            # Create a new cart
            customer = request.user  # Assuming the user is authenticated
            new_cart = Cart.objects.create(customer=customer)

            # Create orders for each item in the cart
            for item_id, item in cart.items():
                product = Product.objects.get(id=item_id)

                product.amount -= item['quantity']
                product.save()

                quantity = item['quantity']
                order = Order.objects.create(cart=new_cart, product=product, quantity=quantity)

            # Redirect to a success page or perform any additional actions
            context = {
                'cart': cart,
            }

            # Clear the cart after creating the orders
            request.session['cart'] = {}
            
            return render(request, 'success_order.html', context)        

    context = {
        'cart': cart,
        'total_price': total_price,
    }

    return render(request, 'cart.html', context)

# @method_decorator([login_required, seller_required], name='dispatch')
# class SellerOrderListView(ListView):
#     model = Order
#     template_name = 'seller_orders.html'
#     context_object_name = 'orders'
#     paginate_by = 10

#     def get_queryset(self):
#         # Filter orders based on the logged-in user (seller)
#         return Order.objects.filter(product__seller=self.request.user).order_by('-order_date')



from itertools import groupby
from operator import attrgetter

# @method_decorator([login_required, seller_required], name='dispatch')
# class SellerOrderListView(ListView):
#     model = Order
#     template_name = 'seller_orders.html'
#     context_object_name = 'cart_orders'
#     paginate_by = 10

#     def get_queryset(self):
#         queryset = Order.objects.filter(product__seller=self.request.user).order_by('-order_date')
#         queryset = queryset.select_related('cart', 'cart__customer', 'product')
#         return queryset

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         orders = context['object_list']
#         grouped_orders = []
        
#         key_func = attrgetter('cart.pk')
#         orders = sorted(orders, key=key_func)
        
#         for cart_pk, cart_orders in groupby(orders, key=key_func):
#             order_list = list(cart_orders)
#             cart_order = {
#                 'cart': order_list[0].cart,
#                 'order_count': len(order_list),
#                 'order_list': order_list
#             }
#             grouped_orders.append(cart_order)
        
#         context['cart_orders'] = grouped_orders
#         return context

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

@method_decorator([login_required, seller_required], name='dispatch')
class SellerOrderListView(ListView):
    model = Order
    template_name = 'seller_orders.html'
    context_object_name = 'cart_orders'
    paginate_by = 10

    def get_queryset(self):
        queryset = Order.objects.filter(product__seller=self.request.user, cart__sent=False).order_by('-order_date')
        queryset = queryset.select_related('cart', 'cart__customer', 'product')
        return queryset

    def post(self, request, *args, **kwargs):
        if 'sent_button' in request.POST:
            cart_id = request.POST.get('cart_id')
            cart = get_object_or_404(Cart, id=cart_id)
            cart.sent = True
            cart.save()
            return HttpResponseRedirect(reverse('seller_orders'))
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = context['object_list']
        grouped_orders = []

        key_func = attrgetter('cart.pk')
        orders = sorted(orders, key=key_func)

        for cart_pk, cart_orders in groupby(orders, key=key_func):
            order_list = list(cart_orders)
            cart_order = {
                'cart': order_list[0].cart,
                'order_count': len(order_list),
                'order_list': order_list
            }
            grouped_orders.append(cart_order)

        context['cart_orders'] = grouped_orders
        return context



