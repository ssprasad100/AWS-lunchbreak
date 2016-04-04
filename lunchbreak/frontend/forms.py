from business.models import Staff
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField


class PlaceholderMixin(object):

    def __init__(self, *args, **kwargs):
        super(PlaceholderMixin, self).__init__(*args, **kwargs)
        has_help_texts = hasattr(self.Meta, 'help_texts')

        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                placeholder = self.Meta.help_texts[field_name] \
                    if has_help_texts and field_name in self.Meta.help_texts \
                    else field.help_text
                field.widget.attrs.update(
                    {
                        'placeholder': placeholder
                    }
                )


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


class StaffForm(PlaceholderMixin, forms.ModelForm):

    inventory_file = forms.FileField(
        required=False,
        label=_('Upload inventory.'),
        help_text=_('Upload inventory.'),
    )

    def clean_inventory_file(self):
        file = self.cleaned_data.get('inventory_file', None)
        if file is None:
            return

        if file.content_type not in [
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]:
            raise ValidationError(
                _(
                    'You can only upload Excel (".xls", ".xlsx") files, please '
                    'download our template.'
                )
            )

    class Meta:
        model = Staff
        fields = ['email', 'first_name', 'last_name']


class CustomAuthenticationForm(PlaceholderMixin, AuthenticationForm):

    class Meta:
        help_texts = {
            'username': _('Email address'),
            'password': _('Password')
        }
