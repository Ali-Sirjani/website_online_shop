from django.contrib import admin
from django.db import models
from django.forms import NumberInput, Textarea


from .models import Product, Category, ProductComment
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


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'datetime_created', 'datetime_modified', 'active')
    ordering = ('-datetime_modified', )
    form = ProductFormAdmin
    inlines = (ProductCommentTabu, )
    formfield_overrides = {
        models.PositiveIntegerField: {'widget': NumberInput()}
    }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

