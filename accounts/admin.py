from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import reverse
from django.utils.http import urlencode

from .models import SetUsername, Profile


@admin.register(SetUsername)
class SetUsernameAdmin(admin.ModelAdmin):
    fields = ('user', 'first_time')
    list_display = ('user', 'first_time')
    list_editable = ('first_time', )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if obj:
            readonly_fields.append('user')

        return readonly_fields


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fields = ('user', 'location', 'first_name', 'last_name', 'phone', 'picture',
              'datetime_created', 'datetime_modified')
    list_display = ('user', 'full_name', 'num_of_user_orders')
    autocomplete_fields = ('user',)
    ordering = ('-datetime_created', )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['datetime_created', 'datetime_modified', ]
        if obj:
            readonly_fields.append('user')

        return readonly_fields

    def full_name(self, obj):
        name = f'{obj.first_name} {obj.last_name}'
        if name and not name.isspace():
            return name

        return None

    def num_of_user_orders(self, obj):
        url = (reverse('admin:cart_order_changelist') + '?' + urlencode({'customer_id': obj.user.pk}))
        return format_html('<a href="{}">{}</a>', url, obj.user.order.count())
