from gocardless_pro.resources import Event

from .exceptions import UnsupportedEventError, UnsupportedLinksError
from .signals import *  # NOQA
from .utils import model_from_links


class EventHandler(object):

    ACTIONS = {
        'mandates': {
            'created': mandate_created,
            'submitted': mandate_submitted,
            'active': mandate_active,
            'reinstated': mandate_reinstated,
            'transferred': mandate_transferred,
            'cancelled': mandate_cancelled,
            'failed': mandate_failed,
            'expired': mandate_expired,
            'resubmission_requested': mandate_resubmission_requested,
        },
        'payments': {
            'created': payment_created,
            'submitted': payment_submitted,
            'confirmed': payment_confirmed,
            'cancelled': payment_cancelled,
            'failed': payment_failed,
            'charged_back': payment_charged_back,
            'chargeback_cancelled': payment_chargeback_cancelled,
            'paid_out': payment_paid_out,
            'late_failure_settled': payment_late_failure_settled,
            'chargeback_settled': payment_chargeback_settled,
            'resubmission_requested': payment_resubmission_requested,
        },
        'subscriptions': {
            'created': subscription_created,
            'payment_created': subscription_payment_created,
            'cancelled': subscription_cancelled,
        },
        'payouts': {
            'paid': payout_paid,
        },
        'refunds': {
            'created': refund_created,
            'paid': refund_paid,
            'refund_settled': refund_settled,
        }
    }

    def __init__(self, event):
        if not isinstance(event, Event):
            raise ValueError('The EventHandler needs to be provided with an Event object.')

        if event.resource_type not in self.ACTIONS:
            raise UnsupportedEventError(
                'Unsupported resource_type: {type}'.format(
                    type=event.resource_type
                )
            )

        actions = self.ACTIONS[event.resource_type]

        if event.action not in actions:
            raise UnsupportedEventError(
                'Unsupported action: {action}'.format(
                    action=event.action
                )
            )

        signal = actions[event.action]
        arguments = {}

        for arg in signal.providing_args:
            try:
                arguments[arg] = model_from_links(event.links, arg)
            except UnsupportedLinksError:
                continue

        signal.send(
            sender=self.__class__,
            event=event,
            **arguments
        )
