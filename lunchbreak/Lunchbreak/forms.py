from django import forms
from .mixins import CleanModelMixin


class FatModelForm(forms.ModelForm):

    def _clean_fields(self):
        super()._clean_fields()

        assert issubclass(self._meta.model, CleanModelMixin)
        instance = self._meta.model(
            **self.cleaned_data,
            **getattr(self, 'instance_data', {})
        )
        instance.clean(form=self)
