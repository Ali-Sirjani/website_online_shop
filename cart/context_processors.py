from .models import Order
from .cart import Cart


def cart(request):
    if request.user.is_authenticated:
        cart_order, created = Order.objects.get_or_create(customer=request.user, completed=False)
    else:
        cart_order = Cart(request)
    context = {
        'cart': cart_order,
    }

    return context
