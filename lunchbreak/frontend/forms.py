from django import forms
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField


class TrialForm(forms.Form):
    company = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'class': 'text',
                'placeholder': _('Company')
            }
        )
    )
    country = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'class': 'text',
                'placeholder': _('Country')
            }
        )
    )
    city = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'class': 'text',
                'placeholder': _('City'),
            }
        )
    )
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'class': 'text',
                'placeholder': _('Email address'),
            }
        )
    )
    phone = PhoneNumberField(
        widget=forms.TextInput(
            attrs={
                'class': 'text',
                'placeholder': _('Phone number'),
            }
        )
    )
