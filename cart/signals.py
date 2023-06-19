from django.contrib.auth.signals import user_logged_in
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .cart import Cart
from .models import Order, OrderItem


def add_item_to_cart_from_session(sender, user, request, **kwargs):
    if request.session.get('cart'):

        cart = Cart(request)
        order, create = Order.objects.get_or_create(customer=user, completed=False)
        for item_session in cart:
            item, create = OrderItem.objects.get_or_create(
                product=item_session['product'],
                order=order,
            )

            if create:
                item.quantity = item_session['quantity']
                item.save()

            else:
                item.quantity += item_session['quantity']
                item.save()

        messages.success(request, _('The product add to your cart'))
        cart.clear_cart()


user_logged_in.connect(add_item_to_cart_from_session)
