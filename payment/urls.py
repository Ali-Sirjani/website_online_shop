from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'payment'


urlpatterns = [
    path('process/checkout/', views.sandbox_process_payment, name='sandbox_process'),
    path('process/callback/', views.sandbox_callback_payment, name='sandbox_callback'),
    path('test/success/', TemplateView.as_view(template_name='payment/success.html')),
    path('test/fail/', TemplateView.as_view(template_name='payment/fail.html')),
    path('test/again/', TemplateView.as_view(template_name='payment/again.html')),
]

