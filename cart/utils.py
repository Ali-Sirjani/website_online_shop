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

    form_order = OrderForm(request.POST or None, instance=order)
    form_shipping = ShippingAddressForm(request.POST or None)
    if form_order.is_valid():
        form_order_obj = form_order.save(commit=False)
        form_order_obj.customer = customer
        transaction_id = datetime.datetime.now().timestamp()
        order.transaction = transaction_id

        # for test total
        total = None
        try:
            total = int(form_order.cleaned_data['total'])
        except ValueError:
            messages.error(request, _('You change the data of checkout form!'))

        if total == order.get_cart_total:
            # save total price
            form_order_obj.order_price = total
            form_order_obj.save()

            # save product price
            for item in order.act_items():
                item.save_price()
                item.backup_product()

            order.backup_total()

            print('this is order in login: ', order.get_cart_total_profit_pass)

        if form_shipping.is_valid():
            if order and order.shipping:
                form_shipping = form_shipping.save(commit=False)
                form_shipping.customer = customer
                form_shipping.order = order
                form_shipping.save()
                return redirect('payment:sandbox_process')

    items = order.act_items().order_by('-datetime_added')

    return form_order, form_shipping, order, items


def save_items_and_shipping_address_user_anonymous(request, cart, order_obj, total, form_shipping):
    order_obj.order_price = total

    for item in cart:
        OrderItem.objects.get_or_create(
            product=item['product'],
            order=order_obj,
            quantity=item['quantity'],
            item_price=item['product'].price,
        )
    # save product price
    for item in order_obj.act_items():
        item.save_price()
        item.backup_product()

    order_obj.backup_total()

    if form_shipping.is_valid():
        if order_obj.shipping:
            try:
                shipping = ShippingAddress.objects.get(order=order_obj)
                form_shipping = ShippingAddressForm(request.POST, instance=shipping)
                if form_shipping.is_valid():
                    form_shipping.save()
            except ShippingAddress.DoesNotExist:
                form_shipping_obj = form_shipping.save(commit=False)
                form_shipping_obj.order = order_obj
                form_shipping_obj.save()

            return True

    return False


def check_out_user_anonymous(request, cart):
    form_order = OrderForm(request.POST or None)
    form_shipping = ShippingAddressForm(request.POST or None)
    if form_order.is_valid():
        email_user = form_order.cleaned_data['email']
        try:
            order_obj = Order.objects.get(customer=None, email=email_user, completed=False)
            request.session['order_pk'] = order_obj.pk

            orders_obj_pk = request.session.get('orders_pk_list')
            if not orders_obj_pk:
                orders_obj_pk = []

            if not (order_obj.pk in orders_obj_pk):
                orders_obj_pk.append(order_obj.pk)
                request.session['orders_pk_list'] = orders_obj_pk

            print('this is request.session: ', request.session['orders_pk_list'])
            form_order = OrderForm(request.POST, instance=order_obj)

            if form_order.is_valid():

                total = None
                try:
                    total = int(form_order.cleaned_data['total'])
                except ValueError:
                    messages.error(request, _('You change the data of checkout form!'))

                if total == cart.get_cart_total:
                    form_order.save()
                    # delete order items for update in save_items_and_shipping_address_user_anonymous()
                    order_obj.items.all().delete()

                    result = save_items_and_shipping_address_user_anonymous(request, cart, order_obj, total,
                                                                            form_shipping)
                    if result:
                        return redirect('payment:sandbox_process')

        except Order.DoesNotExist:
            form_order_obj = form_order.save(commit=False)
            transaction_id = datetime.datetime.now().timestamp()
            form_order_obj.transaction = transaction_id

            total = None
            try:
                total = int(form_order.cleaned_data['total'])
            except ValueError:
                messages.error(request, _('You change the data of checkout form!'))

            if total == cart.get_cart_total:
                form_order_obj.save()

                order_obj = Order.objects.get(customer=None, email=email_user, completed=False)
                request.session['order_pk'] = order_obj.pk

                orders_obj_pk = request.session.get('orders_pk_list')
                if not orders_obj_pk:
                    orders_obj_pk = []

                if not (order_obj.pk in orders_obj_pk):
                    orders_obj_pk.append(order_obj.pk)
                    request.session['orders_pk_list'] = orders_obj_pk
                    # request.session.modified = True
                print('this is request.session: ', request.session['orders_pk_list'])

                result = save_items_and_shipping_address_user_anonymous(request, cart, order_obj, total, form_shipping)
                if result:
                    return redirect('payment:sandbox_process')

    return form_order, form_shipping
