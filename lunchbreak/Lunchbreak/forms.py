from django import forms
from .mixins import CleanModelMixin


class FatModelForm(forms.ModelForm):

    def _post_clean(self):
        assert issubclass(self._meta.model, CleanModelMixin)

        self.instance = self._meta.model(
            **self.cleaned_data,
            **getattr(self, 'instance_data', {})
        )
        self.instance._form = self
        super()._post_clean()
