from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import SetUsername, Profile


@receiver(post_save, sender=get_user_model())
def create_set_username(sender, instance, created, **kwargs):
    if created:
        set_username = SetUsername(user=instance)
        set_username.save()


@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
