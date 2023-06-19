from django.urls import path, re_path

from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductsListView.as_view(), name='products_list'),
    path('search/', views.SearchView.as_view(), name='search_page'),
    path('favorite/<int:pk>/', views.favorite_view, name='favorite'),
    re_path(r'category/(?P<slug>[-\w]+)/', views.CategoryView.as_view(), name='category_page'),
]
