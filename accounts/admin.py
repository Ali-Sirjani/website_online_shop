from django.contrib import admin

from .models import SetUsername, Profile


@admin.register(SetUsername)
class SetUsernameAdmin(admin.ModelAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass
