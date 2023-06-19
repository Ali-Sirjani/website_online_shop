from django.shortcuts import Http404, get_object_or_404, redirect, render
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Product, TimeLike, ProductComment, Category
from .forms import ProductCommentForm, SearchForm
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


class SearchView(generic.ListView):
    paginate_by = 3
    template_name = 'products/search.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = []
        request_get = self.request.GET

        if 'q' in request_get:
            form = SearchForm(request_get)
            if form.is_valid():
                q = form.cleaned_data['q']
                if self.request.LANGUAGE_CODE == 'en':
                    queryset = Product.objects.filter(Q(title__icontains=q) | Q(category__name_en__icontains=q), active=True).distinct('id')
                elif self.request.LANGUAGE_CODE == 'fa':
                    queryset = Product.objects.filter(Q(title__icontains=q) | Q(category__name_fa__icontains=q),
                                                      active=True).distinct('id')

                self.q = q
                sort_num = self.request.GET.get('sort')
                if sort_num:
                    return utils.products_queryset(sort_num, queryset)

        else:
            return render(self.request, 'products/search_q_none.html')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['liked'] = Product.objects.filter(favorite=self.request.user.pk, active=True)
        try:
            context['q'] = self.q
        except AttributeError:
            context['q'] = None
        sort_num = self.request.GET.get('sort')
        if sort_num:
            context['sort'] = f'&sort={sort_num}'
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.GET.get('q'):
            return render(self.request, 'products/search_q_none.html')
        return super().dispatch(request, *args, **kwargs)


# def search_view(request):
#     products = []
#     liked = []
#     page_obj = None
#
#     request_get = request.GET
#
#     if 'q' in request_get:
#         form = SearchForm(request_get)
#         if form.is_valid():
#             page_number = request_get.get("page", 1)
#             q = form.cleaned_data['q']
#             products = Product.objects.filter(title__icontains=q, active=True)
#             liked = Product.objects.filter(favorite=request.user, active=True)
#             paginator = Paginator(products, 3)
#             products = paginator.get_page(page_number)
#
#             context = {
#                 'products': products,
#                 'liked': liked,
#                 'q': q,
#             }
#
#             return render(request, 'products/search.html', context=context)
#
#     return render(request, 'products/search.html')


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


class CategoryView(generic.ListView):
    paginate_by = 3
    template_name = 'products/category.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.filter(Q(category__slug_en=self.kwargs['slug']) | Q(category__slug_fa=self.kwargs['slug']), active=True).distinct('id')

        if queryset.exists():
            sort_num = self.request.GET.get('sort')
            if sort_num:
                return utils.products_queryset(sort_num, queryset)
            return queryset
        else:
            raise Http404(_('There is no product with this address'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['liked'] = Product.objects.filter(favorite=self.request.user.pk, category__slug=self.kwargs['slug'], active=True)
        sort_num = self.request.GET.get('sort')
        if sort_num:
            context['sort'] = f'&sort={sort_num}'
        return context


@method_decorator(login_required, name='post')
class ProductDetailView(generic.edit.FormMixin, generic.DetailView):
    model = Product
    form_class = ProductCommentForm
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if not obj.active:
            raise Http404(_('There is no product with this address'))

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = ProductComment.objects.filter(confirmation=True)
        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        request = self.request

        if form.is_valid():
            comment = form.save(commit=False)
            comment.product = get_object_or_404(Product, pk=self.object.pk)
            comment.author = request.user
            messages.success(request, _('You comment after confirmation will show in comments.'))
            comment.save()
            return redirect(self.object.get_absolute_url())
        else:
            messages.error(request, _('Your comment have problem please try again!'))
            return super().form_invalid(form)
            # return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))
    # def form_invalid(self, form):
    #     return self.render_to_response(self.get_context_data(form=form, errors=form.errors))
