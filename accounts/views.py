from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.db.utils import IntegrityError
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import transaction

from allauth.account.views import PasswordChangeView, PasswordSetView

from cart.models import Order
from .forms import SetUsernameForm, ProfileForm
from .models import Profile
from products.models import Product


class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('general:home')


class CustomPasswordSetView(PasswordSetView):
    success_url = reverse_lazy('general:home')


@login_required
def set_username_view(request):
    user_obj = request.user
    form = SetUsernameForm(request.POST or None)

    if form.is_valid():
        if user_obj.set_username.first_time:
            try:
                with transaction.atomic():
                    user_obj.username = form.cleaned_data['username']
                    user_obj.save()
            except IntegrityError:
                form.add_error('username', 'This username exist!')
                context = {'form': form}
                return render(request, 'accounts/set_username.html', context)

            user_obj.set_username.first_time = False
            user_obj.set_username.save()
            return redirect('general:home')

        else:
            form.add_error('username', _('You changed your username'))

    context = {
        'form': form
    }

    return render(request, 'accounts/set_username.html', context)


class ProfileView(LoginRequiredMixin, generic.UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products_list = Product.objects.filter(favorite=self.request.user.pk, active=True, datetime_like__user=self.request.user.pk).order_by(
            '-datetime_like__datetime_like')
        for product in products_list:
            product.time_like = product.get_time_like(self.request.user)
        context['products'] = products_list
        context['orders_completed'] = Order.objects.filter(customer=self.request.user, completed=True).order_by('-datetime_ordered')

        return context
