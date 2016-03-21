from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField


class TrialForm(forms.Form):
    company = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Company')
            }
        )
    )
    country = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Country')
            }
        )
    )
    city = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'placeholder': _('City'),
            }
        )
    )
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Email address'),
            }
        )
    )
    phone = PhoneNumberField(
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Phone number'),
            }
        )
    )


class CustomAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                placeholder = self.Meta.help_texts[field_name] \
                    if field_name in self.Meta.help_texts else field.help_text
                field.widget.attrs.update(
                    {
                        'placeholder': placeholder
                    }
                )

    class Meta:
        help_texts = {
            'username': _('Email address'),
            'password': _('Password')
        }
