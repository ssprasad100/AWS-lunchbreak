from gocardless_pro.resources import Event

from .signals import *
from .models import Mandate


class EventHandler(object):

    RESOURCE_TYPES = {
        'mandates': {
            'actions': {
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
            'model': Mandate,
            'link': 'mandate',
        }
    }

    def __init__(self, event):
        if not isinstance(event, Event):
            raise ValueError('The EventHandler needs to be provided with an Event object.')

        if event.resource_type not in self.RESOURCE_TYPES:
            raise ValueError('Unsupported resource_type.')

        resource_type = self.RESOURCE_TYPES[event.resource_type]
        actions = resource_type['actions']

        if event.action not in actions:
            raise ValueError('Unsupported action.')

        signal = actions[event.action]
        model = resource_type['model']
        link = resource_type['link']
        identifier = getattr(event.links, link)

        model_instance, created = model.objects.get_or_create(
            id=identifier
        )

        signal.send(
            sender=self.__class__,
            instance=model_instance,
            event=event
        )
