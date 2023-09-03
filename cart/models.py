from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from products.models import Product


class Order(models.Model):
    customer = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='order', null=True,
                                 blank=True, verbose_name=_('customer'))
    first_name = models.CharField(max_length=200, null=True, verbose_name=_('first name'))
    last_name = models.CharField(max_length=200, null=True, verbose_name=_('last name'))
    email = models.EmailField(max_length=254, null=True, verbose_name=_('email'))
    phone = PhoneNumberField(null=True, region='IR', verbose_name=_('phone'))
    order_note = models.TextField(null=True, blank=True, verbose_name=_('order note'))
    completed = models.BooleanField(default=False, blank=True, verbose_name=_('completed'))
    transaction = models.CharField(max_length=200, null=True, verbose_name=_('transaction'))

    datetime_ordered = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime ordered'))
    datetime_payed = models.DateTimeField(null=True, verbose_name=_('datetime payed'))

    # backup
    get_cart_total_no_discount_past = models.PositiveIntegerField(null=True,
                                                                  verbose_name=_('get cart total no discount'))
    get_cart_total_discount_past = models.PositiveIntegerField(null=True,
                                                               verbose_name=_('get cart total discount'))
    get_cart_total_profit_past = models.PositiveIntegerField(null=True, verbose_name=_('get cart total profit'))
    get_cart_total_past = models.PositiveIntegerField(null=True, verbose_name=_('get cart total'))
    get_cart_items_past = models.PositiveIntegerField(null=True, verbose_name=_('get cart total'))

    def __str__(self):
        return str(self.id)

    def act_items(self):
        return self.items.filter(product__active=True)

    def del_in_act_items(self):
        return self.items.filter(product__active=False).delete()

    def backup_total(self):
        self.get_cart_total_no_discount_past = self.get_cart_total_no_discount
        self.get_cart_total_discount_past = self.get_cart_total_discount
        self.get_cart_total_profit_past = self.get_cart_total_profit
        self.get_cart_total_past = self.get_cart_total
        self.get_cart_items_past = self.get_cart_items
        self.save()

    @property
    def get_cart_items(self):
        return sum([item.quantity for item in self.act_items()])

    @property
    def get_cart_total_no_discount(self):
        return sum([item.get_total_no_discount for item in self.act_items()])

    @property
    def get_cart_total_discount(self):
        return sum([item.get_total_discount for item in self.act_items()])

    @property
    def get_cart_total_profit(self):
        return sum([item.get_total_profit for item in self.act_items()])

    @property
    def get_cart_total(self):
        return self.get_cart_total_no_discount - self.get_cart_total_profit

    @property
    def shipping(self):
        shipping = False
        for i in self.act_items():
            if not i.product.digital:
                shipping = True
        return shipping

    def format_time_ordered(self):
        return self.datetime_ordered.strftime('%B %d, %Y')

    def format_time_payed(self):
        return self.datetime_payed.strftime('%B %d, %Y')

    @property
    def avg_track_items(self):
        try:
            avg = sum([item.track_order for item in self.items.all()]) / len(self.items.all())
        except ZeroDivisionError:
            return 'zero'
        if 0 <= avg <= 20:
            return _('Paid')
        if 21 <= avg <= 40:
            return _('Processing')
        if 41 <= avg <= 99:
            return _('Out for delivery')
        if avg == 100:
            return _('Delivered')


class OrderItem(models.Model):
    class Meta:
        ordering = ('datetime_added', )

    TRACK_ORDER_CHOICES = (
        (20, 'Payed'),
        (40, 'Processing'),
        (80, 'Out for delivery'),
        (100, 'Delivered'),
    )
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('product'))
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, related_name='items', null=True, blank=True,
                              verbose_name=_('order'))
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name=_('quantity'))
    track_order = models.PositiveIntegerField(default=0, blank=True, choices=TRACK_ORDER_CHOICES)

    datetime_added = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime added'))

    # backup
    get_total_no_discount_past = models.PositiveIntegerField(null=True, verbose_name=_('get cart total no discount'))
    get_total_discount_past = models.PositiveIntegerField(null=True, verbose_name=_('get cart total discount'))
    get_total_profit_past = models.PositiveIntegerField(null=True, verbose_name=_('get cart total profit'))
    get_total_past = models.PositiveIntegerField(null=True, verbose_name=_('get cart total'))

    item_title = models.CharField(max_length=300, null=True, verbose_name=_('title'))
    item_cover = models.ImageField(upload_to='product_covers/', null=True, verbose_name=_('cover'))
    item_price = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name=_('price'))
    item_digital = models.BooleanField(default=False, null=True, blank=True, verbose_name=_('digital'))
    item_discount = models.BooleanField(default=False, verbose_name=_('discount'))
    item_discount_price = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('discount price'))

    def __str__(self):
        try:
            order_item_str = str(f'order number: {self.order.pk}')
        except AttributeError:
            order_item_str = str(f'order item number: {self.pk} (the order item\'s is deleted)')
        return order_item_str

    def backup_product(self):
        self.item_title = self.product.title
        self.item_cover = self.product.cover
        self.item_price = self.product.price
        self.item_digital = self.product.digital
        self.item_discount = self.product.discount
        self.item_discount_price = self.product.discount_price

        self.get_total_no_discount_past = self.get_total_no_discount
        self.get_total_discount_past = self.get_total_discount
        self.get_total_profit_past = self.get_total_profit
        self.get_total_past = self.get_total
        self.save()

    def save_price(self):
        self.item_price = self.product.price
        self.save()

    @property
    def get_total_no_discount(self):
        return self.product.price * self.quantity

    @property
    def get_total_discount(self):
        if self.product.discount:
            return self.product.discount_price * self.quantity
        return 0

    @property
    def get_total_profit(self):
        if self.product.discount:
            return self.get_total_no_discount - self.get_total_discount
        return 0

    @property
    def get_total(self):
        return self.get_total_no_discount - self.get_total_profit


class ShippingAddress(models.Model):
    customer = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, blank=True, null=True,
                                 verbose_name=_('customer'))
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('order'))
    state = models.CharField(max_length=200, null=True, verbose_name=_('state'))
    city = models.CharField(max_length=200, null=True, verbose_name=_('city'))
    address = models.TextField(null=True, verbose_name=_('address'))
    plate = models.PositiveIntegerField(null=True, verbose_name=_('plate'))
    datetime_added = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime added'))

    def __str__(self):
        return self.address
