from django import forms

from phonenumber_field.widgets import PhoneNumberPrefixWidget

from .models import Profile


class SetUsernameForm(forms.Form):
    username = forms.CharField(max_length=100)


class ProfileForm(forms.ModelForm):
    class Meta:
        REGION_CHOICE = (
            ('IR', '+98'),
            ('US', '+1'),
        )
        
        model = Profile
        fields = ('first_name', 'last_name', 'picture', 'location', 'phone')

        widgets = {
            'picture': forms.FileInput,
            'phone': PhoneNumberPrefixWidget(country_choices=REGION_CHOICE),
        }
