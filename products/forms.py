from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Product, ProductComment


class ProductFormAdmin(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('title', 'description', 'short_description', 'cover', 'category',
                  'price', 'discount', 'discount_price', 'slug_change', 'slug', 'active')
        widgets = {
            'short_description': forms.Textarea(attrs={'cols': 75, 'rows': 5})
        }

    def clean(self):
        clean_data = super().clean()
        price = clean_data['price']
        discount = clean_data['discount']
        discount_price = clean_data['discount_price']

        if not discount:
            clean_data['discount_price'] = None

        elif discount and discount_price is None:
            self.add_error('discount_price', _('You must fill out discounts price because you active discount'))

        elif price <= discount_price:
            self.add_error('discount_price', _('The equal of discount price must be less than from price'))

        return clean_data


class ProductCommentForm(forms.ModelForm):
    class Meta:
        model = ProductComment
        fields = ('text', 'star')


class SearchForm(forms.Form):
    q = forms.CharField()
