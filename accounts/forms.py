from django import forms


class SetUsernameForm(forms.Form):
    username = forms.CharField(max_length=100)
