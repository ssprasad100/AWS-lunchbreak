from gocardless_pro.resources import Event

from .exceptions import UnsupportedEvent
from .signals import *


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
        }
    }

    def __init__(self, event):
        if not isinstance(event, Event):
            raise ValueError('The EventHandler needs to be provided with an Event object.')

        if event.resource_type not in self.ACTIONS:
            raise UnsupportedEvent('Unsupported resource_type: ' + event.resource_type)

        actions = self.ACTIONS[event.resource_type]

        if event.action not in actions:
            raise UnsupportedEvent('Unsupported action: ' + event.action)

        signal = actions[event.action]
        arguments = {}

        for link in signal.providing_args:
            if link not in LINK_MODELS:
                continue

            identifier = getattr(event.links, link)
            argument_model = LINK_MODELS[link]

            if isinstance(argument_model, dict):
                model = argument_model['model']
                where = {
                    argument_model['id_field']: identifier
                }
                argument = argument_model['argument']
            else:
                model = argument_model
                where = {
                    'id': identifier
                }
                argument = link

            if identifier is not None:
                model_instance, created = model.objects.get_or_create(
                    **where
                )
            else:
                model_instance = None

            arguments[argument] = model_instance

        signal.send(
            sender=self.__class__,
            event=event,
            **arguments
        )
