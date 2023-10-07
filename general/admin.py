from django.contrib import admin

from .models import ContactUsModel


@admin.register(ContactUsModel)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'datetime_created', 'answer',)
    ordering = ('answer', '-datetime_created',)
    fields = ('full_name', 'phone', 'email_user', 'message', 'answer', 'datetime_created', 'datetime_modified',)
    readonly_fields = ('datetime_created', 'datetime_modified',)
    list_filter = ('answer', )
    search_fields = ('full_name', 'phone', 'email_user',)

