from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ContactUsModel


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUsModel
        fields = ('full_name', 'email_user', 'phone', 'message')

    def clean(self):
        clean_data = super().clean()
        try:
            email_user = clean_data['email_user']
        except KeyError:
            email_user = 1

        try:
            phone = clean_data['phone']
        except KeyError:
            phone = 1

        if not (email_user or phone):
            self.add_error(None, _('You must fill email or phone'))

        return clean_data

