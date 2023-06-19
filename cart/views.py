from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

import json

from .cart import Cart
from .models import Order, OrderItem
from products.models import Product


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
