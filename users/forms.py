from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from common.models import TranslationEntry


class UserLoginForm(AuthenticationForm):
    """
    Form for user authentication
    """

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'User name',
            'autofocus': True,
        }
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        }
    ))


class PasswordChangeForm(forms.Form):
    new = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'New Password',
        }
    ))
    confirmed = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password',
        }
    ))

    def clean(self):
        cleaned_data = super().clean()
        new = cleaned_data.get('new')
        confirmed = cleaned_data.get('confirmed')
        if new != confirmed:
            raise ValidationError(TranslationEntry.get('PASSWORDS_NOT_IDENTICAL'))

        validate_password(new)
        return self.cleaned_data


class UserDetailsForm(forms.ModelForm):
    class Meta:
        fields = ('first_name','last_name','username','email')
        model = User