from django.db import models
from django.utils.translation import ugettext as _
from django_gocardless.models import RedirectFlow

from ..config import (ORDER_STATUSES_ACTIVE, PAYMENT_METHOD_CASH,
                      PAYMENT_METHOD_GOCARDLESS)
from ..exceptions import GoCardlessDisabled


class PaymentLink(models.Model):

    class Meta:
        unique_together = ('user', 'store',)
        verbose_name = _('betalingskoppeling')
        verbose_name_plural = _('betalingskoppelingen')

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name=_('gebruiker'),
        help_text=_('Gebruiker.')
    )
    store = models.ForeignKey(
        'lunch.Store',
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=_('Winkel.')
    )

    redirectflow = models.ForeignKey(
        'django_gocardless.RedirectFlow',
        on_delete=models.CASCADE,
        verbose_name=_('doorverwijzing'),
        help_text=_(
            'GoCardless doorverwijzing voor het tekenen van een mandaat.'
        )
    )

    @classmethod
    def create(cls, user, store, instance=None, **kwargs):
        if not store.staff.gocardless_ready:
            raise GoCardlessDisabled()

        if instance is None:
            cls.objects.filter(
                user=user,
                store=store
            ).delete()
        elif isinstance(instance, cls):
            instance.delete()

        redirectflow = RedirectFlow.create(
            description=_('Lunchbreak'),
            merchant=store.staff.gocardless,
            **kwargs
        )

        return cls.objects.create(
            user=user,
            store=store,
            redirectflow=redirectflow
        )

    @staticmethod
    def post_delete(sender, instance, using, **kwargs):
        instance.redirectflow.delete()

        updated_orders = instance.user.order_set.filter(
            status__in=ORDER_STATUSES_ACTIVE,
            payment_method=PAYMENT_METHOD_GOCARDLESS
        ).update(
            payment_method=PAYMENT_METHOD_CASH
        )
        if updated_orders > 0:
            instance.user.notify(
                _(
                    'Uw bankrekening werd door ons systeem geweigerd en '
                    'verwijderd. Lopende bestellingen zijn nu contant te '
                    'betalen.'
                )
            )
            instance.store.staff.notify(
                _(
                    'De online betaling van %(user)s is geweigerd. De lopende '
                    'bestellingen hiervan zijn aangepast naar contant.'
                ) % {
                    'user': instance.user.name
                }
            )

    def __str__(self):
        return '{user}, {store}'.format(
            user=self.user,
            store=self.store
        )
