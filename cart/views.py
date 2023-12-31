from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.views import generic
import json

from .models import Order, OrderItem
from products.models import Product
from .cart import Cart
from . import utils


def update_item(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        messages.warning(request, _('Oops! Something went wrong with your request. Please try again.'
                                    ' If the issue persists, contact our support team for assistance.'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    quantity = data.get('quantity')
    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1

    if quantity != 0:
        customer = request.user
        product_id = data['productId']
        action = data['action']

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
            return orders
        except TypeError:
            orders_pk_list = []
            return orders_pk_list

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return reverse('accounts:profile')

        return super().dispatch(request, *args, **kwargs)


class OrderDetailView(generic.DetailView):
    template_name = 'cart/order_detail.html'
    context_object_name = 'order_finished'

    def get_object(self, queryset=None):
        order_pk = self.kwargs.get('pk')
        if self.request.user.is_authenticated:
            order = get_object_or_404(Order, pk=order_pk, customer=self.request.user, completed=True)

        else:
            order = None

        return order

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, _('for see order detail please login with email you ordered.'))
            return redirect('account_login')

        return super().dispatch(request, *args, **kwargs)
