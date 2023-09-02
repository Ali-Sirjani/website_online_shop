from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .cart import Cart
from .models import Order, OrderItem


@receiver(user_logged_in)
def add_item_to_cart_from_session(sender, user, request, **kwargs):
    if request.session.get('cart'):

        cart = Cart(request)
        order, create = Order.objects.get_or_create(customer=user, completed=False)
        for item_session in cart:
            product = item_session.get('product')

            if product.active:
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


@receiver(user_logged_in)
def set_user_for_order_with_customer_null(sender, user, request, **kwargs):
    orders_with_user_email_completed = Order.objects.filter(customer=None, email=user.email, completed=True)

    if orders_with_user_email_completed.exists():
        orders_with_user_email_completed.update(customer=user)

    orders_with_user_email_uncompleted = Order.objects.filter(customer=None, email=user.email, completed=False)

    if orders_with_user_email_uncompleted.exists():
        orders_with_user_email_uncompleted.delete()
