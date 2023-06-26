from django.utils.text import slugify
from random import randint
from datetime import datetime, timedelta

from .models import Product, Category


def products_queryset(sort_num, products):
    products_sort = []
    if sort_num:
        if sort_num == '1':
            products_sort = products.order_by('price')
        if sort_num == '2':
            products_sort = products.order_by('-price')
        if sort_num == '3':
            products_sort = products.order_by('-datetime_created')
        if sort_num == '4':
            products_sort = products.order_by('datetime_created')

    return products_sort


def create_products(request):
    category_count = Category.objects.count()

    for i in range(1, 5001):
        title = f"Product {i}"
        description = f"This is the description for Product {i}"
        short_description = f"Short description for Product {i}"
        cover = f"product_covers/cover_{i}.jpg"
        price = randint(10, 100)
        discount = bool(randint(0, 1))
        discount_price = price - randint(1, 5)
        discount_timer = datetime.now() + timedelta(days=randint(1, 30))
        active = bool(randint(0, 1))
        slug = slugify(title)

        product = Product.objects.create(
            title=title,
            description=description,
            short_description=short_description,
            cover=cover,
            price=price,
            discount=discount,
            discount_price=discount_price,
            discount_timer=discount_timer,
            active=active,
            slug=slug
        )

        # Add random categories to the product
        categories = Category.objects.order_by('?')[:randint(1, 3)]
        product.category.set(categories)
        product.favorite.add(request.user)
        # Save the product
        product.save()

        print(f"Created Product {i}")

