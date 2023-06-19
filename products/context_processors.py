from .models import Category


def products(request):
    sort_dict = {'Cheap': 1, 'Expensive': 2, 'Newest': 3, 'Oldest': 4}
    context = {
        'sort_dict': sort_dict,
        'categories': Category.objects.all(),
    }
    return context