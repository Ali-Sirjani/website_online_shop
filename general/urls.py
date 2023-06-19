from django.urls import path

from . import views


app_name = 'general'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('contact-with-us/', views.ContactUsView.as_view(), name='contact_us')
]

