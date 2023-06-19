from django.contrib import admin

from .models import SetUsername


@admin.register(SetUsername)
class SetUsernameAdmin(admin.ModelAdmin):
    pass
