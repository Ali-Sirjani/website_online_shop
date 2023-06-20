from django.contrib import admin
from django.db import models
from django.forms import Textarea, NumberInput

from jalali_date.admin import ModelAdminJalaliMixin
from modeltranslation.admin import TranslationAdmin

from .models import Product, ProductComment, Category
from .forms import ProductFormAdmin


class ProductCommentTabu(admin.TabularInline):
    model = ProductComment
    readonly_fields = ('datetime_modified', )
    fields = ('author', 'text', 'confirmation', 'datetime_modified')
    ordering = ('-datetime_modified', )
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'cols': 70, 'row': 5})}
    }


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    fields = ('name_en', 'name_fa', 'slug_change', 'slug_en', 'slug_fa')


@admin.register(Product)
class ProductAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ('title', 'price', 'datetime_created', 'datetime_modified', 'active')
    ordering = ('-datetime_modified', )
    form = ProductFormAdmin
    inlines = (ProductCommentTabu, )
    formfield_overrides = {
        models.PositiveIntegerField: {'widget': NumberInput()}
    }
