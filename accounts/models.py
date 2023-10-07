from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model


class SetUsername(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='set_username')
    first_time = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile', verbose_name=_('User'))
    location = models.TextField(blank=True, verbose_name=_('Location'))
    first_name = models.CharField(max_length=200, blank=True, verbose_name=_('First name'))
    last_name = models.CharField(max_length=200, blank=True, verbose_name=_('Last name'))
    phone = PhoneNumberField(unique=True, blank=True, null=True, region='', verbose_name=_('phone'))
    picture = models.ImageField(upload_to='accounts_pictures/', blank=True, null=True, verbose_name=_('picture'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_modified = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime modified'))

    def __str__(self):
        return self.user.username
