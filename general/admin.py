from django.contrib import admin

from .models import ContactUsModel


@admin.register(ContactUsModel)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'message', 'datetime_created', 'answer')
    ordering = ('answer', '-datetime_created')

