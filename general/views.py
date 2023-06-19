from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .forms import ContactUsForm


class HomePageView(generic.TemplateView):
    template_name = 'general/home.html'


class ContactUsView(generic.CreateView):
    form_class = ContactUsForm
    template_name = 'general/contact_us.html'

    def get_success_url(self):
        messages.success(self.request, _('We will soon answer your message'))
        return reverse_lazy('general:home')


