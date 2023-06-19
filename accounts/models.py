from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class SetUsername(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='set_username')
    first_time = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


def create_set_username(sender, instance, created, **kwargs):
    if created:
        set_username = SetUsername(user=instance)
        set_username.save()


models.signals.post_save.connect(create_set_username, sender=get_user_model())
