from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext as _

from .mixins import CleanModelMixin


class FatModelForm(forms.ModelForm):

    def _post_clean(self):
        assert issubclass(self._meta.model, CleanModelMixin)

        self.instance = self.create_instance(
            **self.cleaned_data,
            **getattr(self, 'instance_data', {})
        )
        self.instance._form = self
        super()._post_clean()

    def create_instance(self, **kwargs):
        return self._meta.model(**kwargs)


class PasswordChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=_('Wachtwoord')
    )
    password1 = forms.CharField(
        label=_('Nieuw wachtwoord'),
        widget=forms.PasswordInput,
        required=False
    )
    password2 = forms.CharField(
        label=_('Bevestig wachtwoord'),
        widget=forms.PasswordInput,
        required=False
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError(
                _('Wachtwoorden komen niet overeen.')
            )
        return password2

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get('password')

    def save(self, commit=True):
        instance = super().save(commit=False)

        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            instance.set_password(self.cleaned_data['password1'])
            if commit:
                instance.save()
        return instance
