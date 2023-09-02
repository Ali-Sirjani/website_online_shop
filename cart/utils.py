from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import datetime

from .forms import OrderForm, ShippingAddressForm
from .models import Order, OrderItem, ShippingAddress


def check_out_user_login(request):
    customer = request.user
    order, created = Order.objects.get_or_create(customer=customer, completed=False)

    order.del_in_act_items()
    if order.get_cart_items == 0:
        messages.info(request, _('The Your cart is empty! Please first add some product in your cart.'))
        return redirect('products:products_list')

    shipping, create = ShippingAddress.objects.get_or_create(customer=customer, order=order)

    form_order = OrderForm(request.POST or None, instance=order)
    form_shipping = ShippingAddressForm(request.POST or None, instance=shipping)

    if form_order.is_valid():

        if not order.transaction:
            transaction_id = datetime.datetime.now().timestamp()
            form_order.instance.transaction = transaction_id

        # for test total
        total = None
        try:
            total = int(form_order.cleaned_data.get('total'))
        except ValueError:
            messages.error(request, _('You change the data of checkout form!'))

        if total == order.get_cart_total:
            form_order.save()

            # save product price
            for item in order.act_items():
                item.save_price()
                item.backup_product()

            order.backup_total()

            if form_shipping.is_valid():
                if order.shipping:
                    form_shipping.save()
                    return redirect('payment:sandbox_process')

        else:
            messages.info(request, _('Something went wrong! Please try again.'))

    items = order.act_items().order_by('-datetime_added')

    return form_order, form_shipping, order, items


def check_out_user_anonymous(request, cart):
    if cart.get_cart_items() == 0:
        messages.info(request, _('The Your cart is empty! Pleas first add some product in your cart.'))
        return redirect('products:products_list')

    form_order = OrderForm(request.POST or None)
    form_shipping = ShippingAddressForm(request.POST or None)
    if form_order.is_valid():
        email_user = form_order.cleaned_data.get('email')

        order, create = Order.objects.get_or_create(customer=None, email=email_user, completed=False)

        request.session['order_pk'] = order.pk

        orders_obj_pk = request.session.get('orders_pk_list')
        if not orders_obj_pk:
            orders_obj_pk = []

        if not (order.pk in orders_obj_pk):
            orders_obj_pk.append(order.pk)
            request.session['orders_pk_list'] = orders_obj_pk

        total = None
        try:
            total = int(form_order.cleaned_data.get('total'))
        except ValueError:
            messages.error(request, _('You change the data of checkout form!'))

        if total == cart.get_cart_total:
            form_order = OrderForm(request.POST, instance=order)

            if not order.transaction:
                transaction_id = datetime.datetime.now().timestamp()
                form_order.instance.transaction = transaction_id

            form_order.save()

            # delete order items for update in save_items_and_shipping_address_user_anonymous()
            order.items.all().delete()

            for item in cart:
                OrderItem.objects.create(
                    product=item['product'],
                    order=order,
                    quantity=item['quantity'],
                    item_price=item['product'].price,
                )
            # save product price
            for item in order.act_items():
                item.save_price()
                item.backup_product()

            order.backup_total()

            if form_shipping.is_valid():
                if order.shipping:
                    shipping, create = ShippingAddress.objects.get_or_create(order=order)

                    form_shipping = ShippingAddressForm(request.POST, instance=shipping)
                    form_shipping.save()

                    return redirect('payment:sandbox_process')

        else:
            messages.info(request, _('Something went wrong! Please try again.'))

    return form_order, form_shipping
