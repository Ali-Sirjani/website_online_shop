from .models import Product


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
