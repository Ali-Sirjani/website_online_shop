from django.contrib import admin
from django.db import models
from django.shortcuts import reverse
from django.forms import Textarea, NumberInput
from django.utils.html import format_html
from django.utils.http import urlencode

from jalali_date.admin import ModelAdminJalaliMixin
from modeltranslation.admin import TranslationAdmin

from .models import Product, ProductComment, Category
from .forms import ProductFormAdmin


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    fields = ('name_en', 'name_fa', 'slug_change', 'slug_en', 'slug_fa')
    list_display = ('name_en', 'name_fa', 'products_count',)
    search_fields = ('name_en', 'name_fa',)

    def products_count(self, obj):
        url = (reverse('admin:products_product_changelist') + '?' + urlencode({'category': obj.pk}))
        return format_html('<a href="{}">{}</a>', url, obj.products.count())


class ProductCommentTabu(admin.TabularInline):
    model = ProductComment
    readonly_fields = ('datetime_modified', )
    fields = ('author', 'text', 'confirmation', 'datetime_modified')
    ordering = ('-datetime_modified', )
    extra = 1
    autocomplete_fields = ('author', )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'cols': 70, 'rows': 4})}
    }


@admin.register(Product)
class ProductAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    form = ProductFormAdmin
    list_display = ('title', 'price', 'datetime_created', 'datetime_modified', 'active')
    ordering = ('-datetime_modified', )
    search_fields = ('title', )
    autocomplete_fields = ('category', )
    inlines = (ProductCommentTabu, )
    formfield_overrides = {
        models.PositiveIntegerField: {'widget': NumberInput()}
    }


@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    fields = ('product', 'author', 'text', 'star', 'edited', 'confirmation',
              'datetime_created', 'datetime_modified',)

    list_display = ('product', 'star', 'confirmation', 'datetime_modified',)
    ordering = ('datetime_modified',)
    autocomplete_fields = ('product', 'author')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['datetime_created', 'datetime_modified',]
        if obj:
            readonly_fields.extend(['product', 'author'])

        return readonly_fields
