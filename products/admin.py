from django.contrib import admin
from django.db import models
from django.forms import NumberInput


from .models import Product, Category
from .forms import ProductFormAdmin


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'datetime_created', 'datetime_modified', 'active')
    ordering = ('-datetime_modified', )
    form = ProductFormAdmin


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

