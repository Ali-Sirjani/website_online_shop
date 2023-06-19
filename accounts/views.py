from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.db.utils import IntegrityError
from django.contrib.auth.decorators import login_required
from django.db import transaction

from allauth.account.views import PasswordChangeView, PasswordSetView


from .forms import SetUsernameForm


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
            return redirect('home')

        else:
            form.add_error('username', _('You changed your username'))

    context = {
        'form': form
    }

    return render(request, 'accounts/set_username.html', context)
