from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class ContactUsModel(models.Model):
    full_name = models.CharField(max_length=300, verbose_name=_('full name'))
    phone = PhoneNumberField(blank=True, null=True, region='IR', verbose_name=_('phone'))
    email_user = models.EmailField(blank=True, null=True, verbose_name=_('email'))
    message = models.TextField(verbose_name=_('message'))
    answer = models.BooleanField(default=False, verbose_name=_('answer'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_('datetime modified'))

    def __str__(self):
        return self.full_name
