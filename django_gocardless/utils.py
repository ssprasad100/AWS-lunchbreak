from .exceptions import UnsupportedLinks
from .models import (Customer, CustomerBankAccount, Mandate, Merchant, Payment,
                     Payout, Refund, Subscription)

LINKS_MODELS = {
    'mandate': Mandate,
    'customer': Customer,
    'customer_bank_account': CustomerBankAccount,
    'previous_customer_bank_account': CustomerBankAccount,
    'new_customer_bank_account': CustomerBankAccount,
    'organisation': {
        'model': Merchant,
        'id_field': 'organisation_id',
    },
    'payment': Payment,
    'subscription': Subscription,
    'payout': Payout,
    'refund': Refund,
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
        model = argument_model['model']
        where = {
            argument_model['id_field']: identifier
        }
    else:
        model = argument_model
        where = {
            'id': identifier
        }

    if identifier is not None:
        model_instance, created = model.objects.get_or_create(
            **where
        )
    else:
        model_instance = None

    return model_instance
