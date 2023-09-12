from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import datetime
import json
import requests

from cart.models import Order, ShippingAddress, OrderItem
from cart.cart import Cart
from .zarinpal import zarin_errors


# def process_order(request):
#     transaction_id = datetime.datetime.now().timestamp()
#     form_order = OrderForm(request)
#     form_shipping = ShippingAddressForm(request)
#     order = False
#
#     if request.user.is_authenticated:
#         customer = request.user
#         if form_order.is_valid():
#             form_order = form_order.save(commit=False)
#             form_order.customer = customer
#             # for test total
#             order, created = Order.objects.get_or_create(customer=customer, completed=False)
#             order.transaction = transaction_id
#             total = None
#             try:
#                 total = int(form_order.cleaned_data['total'])
#             except ValueError:
#                 messages.error(request, _('You change the data of checkout form!'))
#
#             if total == order.get_cart_total:
#                 # save total price
#                 form_order.order_price = total
#                 # save product price
#                 for item in order.act_items():
#                     item.item_price = item.save_price()
#
#                 form_order.save()
#
#             #     order.first_name = data['form']['first_name']
#             #     order.last_name = data['form']['last_name']
#             #     order.email = data['form']['email']
#             #     order.phone = data['form']['phone']
#             #
#             # order.save()
#     else:
#         customer = None
#         if form_order.is_valid():
#             form_order.save(commit=False)
#             request.session['email'] = form_order.cleaned_data['email']
#             request.session.modified = True
#             order, created = Order.objects.get_or_create(email=form_order.cleaned_data['email'], completed=False)
#             cart = Cart(request)
#             for item in cart:
#                 OrderItem.objects.get_or_create(
#                     product=item['product'].pk,
#                     order=order.pk,
#                     quantity=item['quantity'],
#                     item_price=item['product'].price,
#                 )
#             order.transaction = transaction_id
#             total = None
#             try:
#                 total = int(form_order.cleaned_data['total'])
#             except ValueError:
#                 messages.error(request, _('You change the data of checkout form!'))
#
#             if total == order.get_cart_total:
#                 # save total price
#                 order.order_price = total
#                 # save product price
#                 for item in order.act_items():
#                     item.item_price = item.save_price()
#
#                 form_order.save()
#             #     order.first_name = data['form']['first_name']
#             #     order.last_name = data['form']['last_name']
#             #     order.email = data['form']['email']
#             #     order.phone = data['form']['phone']
#             #
#             # order.save()
#     if form_shipping.is_valid():
#         if order and order.shipping:
#             form_shipping = form_shipping.save(commit=False)
#             form_shipping.customer = customer
#             form_shipping.order = order
#             form_shipping.save()
#
#     return redirect()


# def process_payment(request):
#     customer = request.user
#     order, created = Order.objects.get_or_create(customer=customer, completed=False)
#
#     toman_total = order.get_cart_total
#     rial_total = toman_total * 10
#
#     zarinpal_url = 'https://api.zarinpal.com/pg/v4/payment/request.json'
#
#     request_header = {
#         'accept': 'application/json',
#         'content-type': 'application/json',
#     }
#
#     request_data = {
#         'merchant_id': 'asdfew' * 6,
#         'amount': rial_total,
#         'description': f'order:{order.id}, user:{customer.first_name} {customer.last_name}.',
#         'callback_url': request.build_absolute_uri(reverse('payment:sandbox_callback')),
#     }
#
#     res = requests.post(url=zarinpal_url, data=json.dumps(request_data), headers=request_header)
#     data = res.json()['data']
#
#     authority = data['authority']
#     # order.zarinpal_authority = authority
#     # order.save()
#
#     if 'errors' not in data or len(data['errors']) == 0:
#         return redirect(f'https://www.zarinpal.com/pg/StartPay/{authority}')
#     else:
#         return HttpResponse('fail')
#
#
# def callback_payment(request):
#     payment_authority = request.GET.get('Authority')
#     payment_status = request.GET.get('Status')
#
#     order, created = Order.objects.get_or_create(customer=request.user, completed=False)
#
#     toman_total = order.get_cart_total
#     rial_total = toman_total * 10
#
#     if payment_status == 'OK':
#         request_header = {
#             'accept': 'application/json',
#             'content-type': 'application/json',
#         }
#
#         request_data = {
#             'merchant_id': 'asdfew' * 6,
#             'amount': rial_total,
#             'authority': payment_authority,
#         }
#
#         zarinpal_url_varify = 'https://api.zarinpal.com/pg/v4/payment/verify.json'
#
#         res = requests.post(url=zarinpal_url_varify, data=request_data, headers=request_header)
#         data = res.json()['data']
#
#         if 'errors' not in data or len(data['errors']) == 0:
#             payment_code = data['code']
#
#             if payment_code == 100:
#                 order.completed = True
#                 # order.ref_id = data['ref_id']
#                 # order.zarinpal_data = data
#                 order.save()
#                 return render(request, 'payment/success.html')
#
#             elif payment_code == 101:
#                 return render(request, 'payment/fail.html')
#
#             else:
#                 error_code = data['errors']['code']
#                 error_messages = data['errors']['messages']
#                 messages.warning(request, f'{error_code} {error_messages}')
#                 return render(request, 'payment/fail.html')
#
#         else:
#             return HttpResponse('fail')
#
#     else:
#         return render(request, 'cart/cart.html')


def sandbox_process_payment(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, completed=False)
    else:
        order_pk = request.session.get('order_pk')
        if not order_pk:
            messages.info(request, _('please try again'))
            return redirect('products:products_list')
        try:
            order = Order.objects.get(pk=order_pk)
        except Order.DoesNotExist:
            messages.info(request, _('Your cart is empty!'))
            return redirect('products:products_list')

    toman_total = order.get_cart_total
    rial_total = toman_total * 10

    zarinpal_url = 'https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json'

    request_header = {
        'accept': 'application/json',
        'content-type': 'application/json',
    }

    request_data = {
        'MerchantID': 'asdfew' * 6,
        'Amount': rial_total,
        'Description': f'order:{order.id}',
        'CallbackURL': request.build_absolute_uri(reverse('payment:sandbox_callback')),
    }

    res = requests.post(url=zarinpal_url, data=json.dumps(request_data), headers=request_header)
    data = res.json()
    authority = data['Authority']
    # order.zarinpal_authority = authority
    # order.save()

    if 'errors' not in data or len(data['errors']) == 0:
        return redirect(f'https://sandbox.zarinpal.com/pg/StartPay/{authority}')
    else:
        return render(request, 'payment/success.html')


def sandbox_callback_payment(request):
    payment_authority = request.GET.get('Authority')
    payment_status = request.GET.get('Status')

    user = request.user

    if user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=user, completed=False)
    else:
        order_pk = request.session.get('order_pk')
        order, created = Order.objects.get_or_create(pk=order_pk)

    toman_total = order.get_cart_total
    rial_total = toman_total * 10

    if payment_status == 'OK':
        request_header = {
            'accept': 'application/json',
            'content-type': 'application/json',
        }

        request_data = {
            'MerchantID': 'asdfew' * 6,
            'Amount': rial_total,
            'Authority': payment_authority,
        }

        zarinpal_url_varify = 'https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json'

        res = requests.post(url=zarinpal_url_varify, data=json.dumps(request_data), headers=request_header)
        data = res.json()

        payment_code = data['Status']

        if payment_code == 100:
            if not user.is_authenticated:
                cart_obj = Cart(request)
                cart_obj.clear_cart()

            order.completed = True
            for item in order.items.all():
                item.track_order = 20
                item.save()
            order.datetime_payed = datetime.datetime.now()
            # order.ref_id = data['ref_id']
            # order.zarinpal_data = data
            order.save()
            return render(request, 'payment/success.html')

        return zarin_errors(request, payment_code)

    else:
        return render(request, 'payment/fail.html')
