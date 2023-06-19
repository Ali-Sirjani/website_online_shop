from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.views import generic
import json

from .models import Order, OrderItem
from products.models import Product
from .cart import Cart
from . import utils


def update_item(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']
    quantity = data['quantity']
    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1

    if quantity != 0:
        customer = request.user
        if customer.is_authenticated:
            order, order_created = Order.objects.get_or_create(customer=customer, completed=False)
            if action == 'delete_cart':
                order.items.all().delete()
                messages.success(request, _('Cart deleted'))
                return JsonResponse('finish update view', safe=False)

            product = get_object_or_404(Product, pk=product_id, active=True)

            try:
                item = OrderItem.objects.get(order=order, product=product)
            except OrderItem.DoesNotExist:
                if quantity < 0:
                    return JsonResponse('finish update view', safe=False)
                item = OrderItem.objects.create(order=order, product=product)

            if item.product.active:
                if item.quantity * -1 > quantity or action == 'delete_item':
                    item.delete()
                    messages.success(request, _('Delete product'))
                    return JsonResponse('finish update view', safe=False)

                elif action == 'add' and quantity > 0:
                    item.quantity += quantity
                    messages.success(request, _('Add product'))
                elif action == 'remove':
                    if quantity < 0:
                        quantity *= -1
                    item.quantity -= quantity
                    messages.success(request, _('Remove product'))

                item.save()

                if item.quantity <= 0:
                    item.delete()
                    messages.success(request, _('Delete product'))
        else:
            cart = Cart(request)
            if action == 'delete_cart':
                cart.clear_cart()
                messages.success(request, _('Cart deleted'))
            else:
                cart.update_quantity(product_id, action, quantity)

        return JsonResponse('finish update view', safe=False)

    else:
        messages.warning(request, _('Please enter a correct number!'))

    return JsonResponse('finish 0', safe=False)


def cart_view(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, completed=False)
        items = order.act_items().order_by('-datetime_added')
        order.del_in_act_items()
    else:
        cart = Cart(request)
        order = cart
        items = cart

    context = {
        'order': order,
        'items': items,
    }

    return render(request, 'cart/cart.html', context)


def checkout_view(request):
    # user with account
    if request.user.is_authenticated:
        checkout_login = utils.check_out_user_login(request)
        try:
            form_order, form_shipping, order, items = checkout_login
        except ValueError:
            return checkout_login

    # user without account
    else:
        order = cart = Cart(request)
        items = None
        if cart.get_cart_items() == 0:
            messages.info(request, _('The Your cart is empty! Pleas first add some product in your cart.'))
            return redirect('products:products_list')

        checkout_anonymous = utils.check_out_user_anonymous(request, cart)
        try:
            form_order, form_shipping = checkout_anonymous
        except ValueError:
            return checkout_anonymous

    context = {
        'order': order,
        'items': items,
        'form_order': form_order,
        'form_shipping': form_shipping,
    }

    return render(request, 'cart/checkout.html', context)


class OrderReportAnonymous(generic.ListView):
    context_object_name = 'orders_completed'
    template_name = 'cart/order_anonymous.html'

    def get_queryset(self):
        try:
            orders_pk_list = self.request.session.get('orders_pk_list')
            orders = Order.objects.filter(id__in=orders_pk_list, completed=True)
            print('this is track_order: ', orders.last().avg_track_items)
            return orders
        except TypeError:
            orders_pk_list = []
            return orders_pk_list

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return reverse('accounts:profile')

        return super().dispatch(request, *args, **kwargs)


class OrderDetailView(generic.ListView):
    template_name = 'cart/order_detail.html'
    context_object_name = 'order_finished'

    def get_queryset(self):
        order_pk = self.kwargs['pk']
        if self.request.user.is_authenticated:
            order = get_object_or_404(Order, pk=order_pk, customer=self.request.user, completed=True)
        else:
            orders_pk_list = self.request.session.get('orders_pk_list')
            if orders_pk_list and order_pk in orders_pk_list:
                order = get_object_or_404(Order, pk=self.kwargs['pk'], customer=None, completed=True)
            else:
                raise Http404('there is no order')
        return order

    # def process_order(request):
#     order = False

    # if request.user.is_authenticated:
    #     if form_order.is_valid():
    #         form_order = form_order.save(commit=False)
    #         form_order.customer = customer
    #         # for test total
    #         order, created = Order.objects.get_or_create(customer=customer, completed=False)
    #         order.transaction = transaction_id
    #         total = None
    #         try:
    #             total = int(form_order.cleaned_data['total'])
    #         except ValueError:
    #             messages.error(request, _('You change the data of checkout form!'))
    #
    #         if total == order.get_cart_total:
    #             # save total price
    #             form_order.order_price = total
    #             # save product price
    #             for item in order.act_items():
    #                 item.item_price = item.save_price()
    #
    #             form_order.save()

    # else:
    #     customer = None
    #     if form_order.is_valid():
    #         form_order.save(commit=False)
    #         request.session['email'] = form_order.cleaned_data['email']
    #         request.session.modified = True
    #         order, created = Order.objects.get_or_create(email=form_order.cleaned_data['email'], completed=False)
    #         cart = Cart(request)
    #         for item in cart:
    #             OrderItem.objects.get_or_create(
    #                 product=item['product'].pk,
    #                 order=order.pk,
    #                 quantity=item['quantity'],
    #                 item_price=item['product'].price,
    #             )
    #         order.transaction = transaction_id
    #         total = None
    #         try:
    #             total = int(form_order.cleaned_data['total'])
    #         except ValueError:
    #             messages.error(request, _('You change the data of checkout form!'))
    #
    #         if total == order.get_cart_total:
    #             # save total price
    #             order.order_price = total
    #             # save product price
    #             for item in order.act_items():
    #                 item.item_price = item.save_price()
    #
    #             form_order.save()

