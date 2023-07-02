def cart_quantity(request):
    cart = request.session.get('cart', {})
    quantity = sum(item['quantity'] for item in cart.values())
    return {'cart_quantity': quantity}


from .models import Cart, Product
from django.db.models import Sum

def cart_count(request):
    try:
        current_user = request.user
        current_seller_products = Product.objects.filter(seller=current_user)
        total_unsent_products = current_seller_products.filter(order__cart__sent=False).aggregate(total=Sum('order__quantity'))['total']
        product_count = total_unsent_products if total_unsent_products else 0

        return {'order_unsend': product_count}
    except Exception as e:
        return {'order_unsend': 0}

