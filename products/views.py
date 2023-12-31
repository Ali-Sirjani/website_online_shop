from django.shortcuts import Http404, get_object_or_404, redirect, render, reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Q, F, Case, When, IntegerField

import json

from .models import Product, TimeLike, ProductComment, Category
from .forms import ProductCommentForm, SearchForm
from . import utils


class ProductsListView(generic.ListView):
    template_name = 'products/products_list.html'
    context_object_name = 'products'
    paginate_by = 3

    def get_queryset(self):
        queryset = Product.active_objs.all()
        sort_num = self.request.GET.get('sort')
        if sort_num:
            sort_by = utils.queryset_sort_by(sort_num)

            if 'price' in sort_by:
                queryset = queryset.annotate(
                    effective_price=Case(
                        When(discount=True, then=F('discount_price')),
                        default=F('price'),
                        output_field=IntegerField()
                    )
                )

                if sort_by == 'price':
                    queryset = queryset.order_by('effective_price')

                elif sort_by == '-price':
                    queryset = queryset.order_by('-effective_price')

            else:
                queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['liked'] = Product.active_objs.filter(favorite=self.request.user.pk).values_list('pk', flat=True)
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
                    queryset = Product.active_objs.filter(
                        Q(title__icontains=q) | Q(category__name_en__icontains=q)).distinct()
                elif self.request.LANGUAGE_CODE == 'fa':
                    queryset = Product.active_objs.filter(
                        Q(title__icontains=q) | Q(category__name_fa__icontains=q)).distinct()

                self.q = q
                sort_num = self.request.GET.get('sort')
                if sort_num:
                    sort_by = utils.queryset_sort_by(sort_num)

                    if 'price' in sort_by:
                        queryset = queryset.annotate(
                            effective_price=Case(
                                When(discount=True, then=F('discount_price')),
                                default=F('price'),
                                output_field=IntegerField()
                            )
                        )

                        if sort_by == 'price':
                            queryset = queryset.order_by('effective_price')

                        elif sort_by == '-price':
                            queryset = queryset.order_by('-effective_price')

                    else:
                        queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['liked'] = Product.active_objs.filter(favorite=self.request.user.pk).values_list('pk', flat=True)
        try:
            context['q'] = self.q
        except AttributeError:
            context['q'] = None
        sort_num = self.request.GET.get('sort')
        if sort_num:
            context['sort'] = f'&sort={sort_num}'
        return context

    def dispatch(self, request, *args, **kwargs):
        q = request.GET.get('q')
        if not q or q.isspace():
            return render(self.request, 'products/search_q_none.html')
        return super().dispatch(request, *args, **kwargs)


@require_POST
def favorite_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        messages.warning(request, _('Oops! Something went wrong with your request. Please try again.'
                                    ' If the issue persists, contact our support team for assistance.'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if request.user.is_authenticated:
        pk = data.get('productId')
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

        response = {'authenticated': True}
        return JsonResponse(response, safe=False)
    else:
        response = {'authenticated': False, 'login': request.build_absolute_uri(reverse('account_login'))}
        return JsonResponse(response, safe=False)


class CategoryView(generic.ListView):
    paginate_by = 3
    template_name = 'products/category.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.active_objs.filter(
            Q(category__slug_en=self.kwargs['slug']) | Q(category__slug_fa=self.kwargs['slug'])).distinct()

        sort_num = self.request.GET.get('sort')
        if sort_num:
            sort_by = utils.queryset_sort_by(sort_num)

            if 'price' in sort_by:
                queryset = queryset.annotate(
                    effective_price=Case(
                        When(discount=True, then=F('discount_price')),
                        default=F('price'),
                        output_field=IntegerField()
                    )
                )

                if sort_by == 'price':
                    queryset = queryset.order_by('effective_price')

                elif sort_by == '-price':
                    queryset = queryset.order_by('-effective_price')

            else:
                queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['liked'] = Product.active_objs.filter(favorite=self.request.user.pk).values_list('pk', flat=True)
        sort_num = self.request.GET.get('sort')
        if sort_num:
            context['sort'] = f'&sort={sort_num}'

        if not self.get_queryset().exists():
            try:
                if self.request.LANGUAGE_CODE == 'en':
                    context['category_name'] = Category.objects.get(slug=self.kwargs['slug']).name_en
                elif self.request.LANGUAGE_CODE == 'fa':
                    context['category_name'] = Category.objects.get(slug=self.kwargs['slug']).name_fa
            except Category.DoesNotExist:
                context['category_name'] = self.kwargs['slug'].replace('-', ' ')

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
        context['comments'] = ProductComment.objects.filter(confirmation=True, product=self.object.pk)
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
