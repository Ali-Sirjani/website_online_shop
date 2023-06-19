from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductsListView.as_view(), name='products_list'),
    path('favorite/<int:pk>/', views.favorite_view, name='favorite'),
]
