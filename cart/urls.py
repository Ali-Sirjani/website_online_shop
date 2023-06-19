from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart_page'),
    path('update-item/', views.update_item, name='update_item'),
    path('checkout/', views.checkout_view, name='checkout'),
]
