import copy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Product


class Cart:

    def __init__(self, request):
        self.request = request
        self.session = request.session

        cart = self.session.get('cart')

        if not cart:
            self.cart = self.session['cart'] = {}
        else:
            self.cart = cart
        self.save()

    def __iter__(self):
        products_pk = self.cart.keys()

        cart_products = Product.objects.filter(id__in=products_pk)

        # cart = self.cart.copy()
        cart = copy.deepcopy(self.cart)

        for product in cart_products:
            cart[str(product.pk)]['product'] = product
            cart[str(product.pk)]['get_total_no_discount'] = self.price_one_product_without_discount(product)
            cart[str(product.pk)]['get_total_discount'] = self.price_one_product_with_discount(product)
            cart[str(product.pk)]['get_total_profit'] = self.profit_price(product)
            cart[str(product.pk)]['get_total'] = self.get_total(product)

        for item in cart.values():
            yield item

    def __len__(self):
        return sum([item['quantity'] for item in self.cart.values()])

    def act_items(self):
        return self.__iter__()

    def get_cart_items(self):
        return sum([item['quantity'] for item in self.cart.values()])

    def items_in_cart(self):
        return self.cart.keys()

    def save(self):
        self.session.modified = True

    def update_quantity(self, product_pk, action, quantity=1):
        product_pk_str = str(product_pk)
        if product_pk_str not in self.cart:
            if quantity < 0:
                return
            self.cart[product_pk_str] = {'quantity': 0}

        if self.cart[product_pk_str]['quantity'] * -1 > quantity or action == 'delete_item':
            del self.cart[product_pk_str]
            messages.success(self.request, _('Delete product'))
            self.save()
            return

        elif action == 'add':
            self.cart[product_pk_str]['quantity'] += quantity
            messages.success(self.request, _('Add product'))

        elif action == 'remove':
            self.cart[product_pk_str]['quantity'] -= quantity
            messages.success(self.request, _('Remove product'))

        if self.cart[product_pk_str]['quantity'] <= 0:
            del self.cart[product_pk_str]
            messages.success(self.request, _('Delete product'))

        self.save()

    def clear_cart(self):
        del self.session['cart']
        self.save()

    def price_one_product_without_discount(self, product):
        price = product.price * self.cart[str(product.pk)]['quantity']
        return price

    def price_one_product_with_discount(self, product):
        price = 0
        if product.discount and product.active:
            price = product.discount_price * self.cart[str(product.pk)]['quantity']
        return price

    def profit_price(self, product):
        price = 0
        if product.discount and product.active:
            price = self.price_one_product_without_discount(product) - self.price_one_product_with_discount(product)
        return price

    def get_total(self, product):
        return self.price_one_product_without_discount(product) - self.profit_price(product)

    @property
    def get_cart_total_no_discount(self):
        return sum([self.price_one_product_without_discount(item['product']) for item in self])

    @property
    def get_cart_total_discount(self):
        return sum([self.price_one_product_with_discount(item['product']) for item in self])

    @property
    def get_cart_total_profit(self):
        return sum([self.profit_price(item['product']) for item in self])

    @property
    def get_cart_total(self):
        return sum([self.get_total(item['product']) for item in self])
