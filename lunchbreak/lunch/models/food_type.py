from datetime import time

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from ..config import INPUT_AMOUNT, INPUT_TYPES
from ..exceptions import InvalidFoodTypeAmount


class FoodType(models.Model):

    class Meta:
        verbose_name = _('type etenswaar')
        verbose_name_plural = _('type etenswaren')

    def __str__(self):
        return self.name

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
        help_text=_(
            'Naam van de eenheid van eten, vb: "broodjes", "broden"...'
        )
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
    store = models.ForeignKey(
        'Store',
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=_('Winkel.')
    )
    wait = models.DurationField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_('wachttijd'),
        help_text=_(
            'Minimum tijd dat op voorhand besteld moet worden. Indien dit '
            'niet ingesteld is, dan wordt de wachttijd van de winkel '
            'overgenomen.'
        )
    )
    preorder_time = models.TimeField(
        default=time(hour=12),
        verbose_name=_('tijd voorafgaande bestelling'),
        help_text=_(
            'Indien bepaalde waren meer dan een dag op voorhand besteld moeten '
            'worden, moeten ze voor dit tijdstip besteld worden.'
        )
    )
    preorder_days = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_('dagen op voorhand bestellen'),
        help_text=(
            'Minimum dagen op voorhand bestellen voor het uur ingesteld op '
            'de winkel. (0 is dezelfde dag, >=1 is dat aantal dagen voor het '
            'bepaalde uur.) Indien dit niet ingesteld is, dan is '
            'voorbestellen uitgeschakeld voor dit type etenswaar.'
        )
    )

    @cached_property
    def inherited_wait(self):
        return self.wait \
            if self.wait is not None \
            else self.store.wait

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
