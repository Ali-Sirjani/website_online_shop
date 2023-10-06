from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Order, OrderItem, ShippingAddress


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

    def clean(self):
        clean_data = super().clean()

        if not clean_data.get('completed'):
            try:
                user = clean_data.get('customer')

                order = Order.objects.get(customer=user, completed=False)
                order_pk = order.pk
                self.add_error('customer', _(f'There is an incomplete order with pk {order_pk} for user {user}'))

            except Order.DoesNotExist:
                pass

        elif self.instance:
            try:
                self.instance.address
            except ShippingAddress.DoesNotExist:
                self.add_error(None, _('Complete order must have a shipping address'))

        return clean_data


class OrderItemAdminForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = '__all__'

    def clean(self):
        clean_data = super().clean()
        order = clean_data.get('order')

        if order.completed:
            self.add_error('order', _('This order is complete'))

        return clean_data


class OrderForm(forms.ModelForm):
    total = forms.IntegerField(min_value=0)

    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'email', 'phone', 'order_note')


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ('state', 'city', 'address', 'plate')
