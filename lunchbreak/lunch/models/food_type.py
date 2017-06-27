from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..config import INPUT_AMOUNT, INPUT_TYPES
from ..exceptions import InvalidFoodTypeAmount


class FoodType(models.Model):
    name = models.CharField(
        max_length=191,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )
    quantifier = models.CharField(
        max_length=191,
        blank=True,
        null=True,
        verbose_name=_('eenheid'),
        help_text=_('Naam van de eenheid van eten, vb: "broodjes", "broden"...')
    )
    inputtype = models.PositiveIntegerField(
        choices=INPUT_TYPES,
        default=INPUT_TYPES[0][0],
        verbose_name=_('invoer type'),
        help_text=_(
            'Invoer type die aanduid hoe de hoeveelheid ingegeven moet en '
            'kan worden.'
        )
    )
    customisable = models.BooleanField(
        default=False,
        verbose_name=_('aanpasbaar'),
        help_text=_('Of dit type etenswaar aanpasbaar kan zijn.')
    )

    class Meta:
        verbose_name = _('type etenswaar')
        verbose_name_plural = _('type etenswaren')

    def is_valid_amount(self, amount, quantity=None, raise_exception=True):
        """Check whether the given amount is valid for the foodtype.

        Args:
            amount: Food amount.
            quantity: Quantity model. (default: {None})
            raise_exception: Raise an exception if invalid. (default: {True})

        Returns:
            Valid returns True, invalid returns False.
            bool

        Raises:
            InvalidFoodTypeAmount: Raised if invalid amount.
        """
        is_valid = (
            amount > 0 and (
                self.inputtype != INPUT_AMOUNT or
                float(amount).is_integer()
            ) and (
                quantity is None or
                quantity.minimum <= amount <= quantity.maximum
            )
        )

        if not is_valid and raise_exception:
            raise InvalidFoodTypeAmount()
        return is_valid

    def __str__(self):
        return self.name
