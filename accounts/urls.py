from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('username/set/', views.set_username_view, name='set_username'),
]
