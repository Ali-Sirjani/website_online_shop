from django.views import generic
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from .models import Product, TimeLike
from . import utils


class ProductsListView(generic.ListView):
    paginate_by = 6
    template_name = 'products/products_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.filter(active=True)
        sort_num = self.request.GET.get('sort')
        if sort_num:
            return utils.products_queryset(sort_num, queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['liked'] = Product.objects.filter(favorite=self.request.user.pk, active=True)
        sort_num = self.request.GET.get('sort')
        if sort_num:
            context['sort'] = f'&sort={sort_num}'
        return context


@login_required
def favorite_view(request, pk):
    product_obj = get_object_or_404(Product, pk=pk, active=True)
    user = request.user
    if product_obj.favorite.filter(pk=user.pk).exists():
        product_obj.favorite.remove(user)
        get_object_or_404(TimeLike, user=user, product=product_obj).delete()
        messages.error(request, _('Unlike post.'))
    else:
        product_obj.favorite.add(user)
        time_like, create = TimeLike.objects.get_or_create(user=user, product=product_obj)
        time_like.save()
        messages.success(request, _('Like post.'))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

