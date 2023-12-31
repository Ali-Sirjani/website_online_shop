import random

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Product, Category


@receiver(pre_save, sender=Product)
def create_slug_product(sender, instance, *args, **kwargs):
    if not instance.slug or instance.slug_change:
        instance.slug = create_unique_slug(instance, instance.title)


@receiver(pre_save, sender=Category)
def create_slug_en_category(sender, instance, *args, **kwargs):
    if not instance.slug_en or instance.slug_change:
        instance.slug_en = create_unique_slug(instance, instance.name_en)
        instance.slug_change = False


@receiver(pre_save, sender=Category)
def create_slug_fa_category(sender, instance, *args, **kwargs):
    if not instance.slug_fa or instance.slug_change:
        instance.slug_fa = create_unique_slug(instance, instance.name_fa)
        instance.slug_change = False


def create_unique_slug(instance, create_by, slug_primitive=None):
    if instance.slug_change or slug_primitive is None:
        slug = slugify(create_by, allow_unicode=True)
    else:
        slug = slug_primitive

    ins_class = instance.__class__
    obj = ins_class.objects.filter(slug=slug)

    if obj.exists():
        instance.slug_change = False
        slug = f'{slug}-{random.choice("12345")}'
        return create_unique_slug(instance, create_by, slug)

    return slug
