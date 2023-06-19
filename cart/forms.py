from django import forms

from .models import Order, ShippingAddress


class OrderForm(forms.ModelForm):
    total = forms.IntegerField(min_value=0)

    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'email', 'phone', 'order_note')


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ('state', 'city', 'address', 'plate')
