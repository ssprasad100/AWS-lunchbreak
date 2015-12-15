from django.apps import apps
from django.db import models

from .exceptions import UnsupportedLinks

LINKS_MODELS = {
    'mandate': 'Mandate',
    'customer': 'Customer',
    'customer_bank_account': 'CustomerBankAccount',
    'previous_customer_bank_account': 'CustomerBankAccount',
    'new_customer_bank_account': 'CustomerBankAccount',
    'organisation': {
        'model': 'Merchant',
        'id_field': 'organisation_id',
    },
    'payment': 'Payment',
    'subscription': 'Subscription',
    'payout': 'Payout',
    'refund': 'Refund',
}


def model_from_links(links, attr):
    if attr not in LINKS_MODELS:
        raise UnsupportedLinks(
            '{attr} is not a supported links model.'.format(
                attr=attr
            )
        )

    identifier = links[attr] if type(links) is dict else getattr(links, attr)
    argument_model = LINKS_MODELS[attr]

    if isinstance(argument_model, dict):
        model_name = argument_model['model']
        where = {
            argument_model['id_field']: identifier
        }
    else:
        model_name = argument_model
        where = {
            'id': identifier
        }

    if identifier is not None:
        model = apps.get_model('django_gocardless', model_name)
        model_instance, created = model.objects.get_or_create(
            **where
        )
    else:
        model_instance = None

    return model_instance


def field_default(field):
    cls = field.__class__

    if issubclass(cls, models.CharField) or issubclass(cls, models.TextField):
        return ''
    return None
