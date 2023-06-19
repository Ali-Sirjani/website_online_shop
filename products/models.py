from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ckeditor.fields import RichTextField


class ActiveProductsManager(models.Manager):
    def get_queryset(self):
        return super(ActiveProductsManager, self).get_queryset().filter(active=True)


class Product(models.Model):
    title = models.CharField(max_length=300, verbose_name=_('title'))
    description = RichTextField(verbose_name=_('description'))
    short_description = models.CharField(max_length=300, null=True, blank=True, verbose_name=_('short description'))
    cover = models.ImageField(upload_to='product_covers/', verbose_name=_('cover'))
    favorite = models.ManyToManyField(get_user_model(), related_name='favorites', default=None, blank=True)
    digital = models.BooleanField(default=False, null=True, blank=True, verbose_name=_('digital'))
    price = models.PositiveIntegerField(verbose_name=_('price'))
    discount = models.BooleanField(default=False, verbose_name=_('discount'))
    discount_price = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('discount price'))
    discount_timer = models.DateTimeField(null=True, blank=True, verbose_name=_('discount timer'))
    active = models.BooleanField(default=True, verbose_name=_('active'))
    slug_change = models.BooleanField(default=False, verbose_name=_('slug change'),
                                      help_text=_('If you want change the slug by name'))
    slug = models.SlugField(blank=True, allow_unicode=True, max_length=300, verbose_name=_('slug'),
                            help_text=_('If field be empty it\'s automatic change by name '))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_('datetime modified'))

    def __str__(self):
        return self.title

    def get_time_like(self, user):
        time = TimeLike.objects.get(product=self, user=user)
        datetime_like = time.datetime_like.strftime('%Y-%m-%d %H:%M:%S')
        return datetime_like


class TimeLike(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='datetime_like',
                             verbose_name=_('user'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='datetime_like',
                                verbose_name=_('product'))
    datetime_like = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime like'))

    def __str__(self):
        return str(self.product.pk)
