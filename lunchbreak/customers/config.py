from django.utils.translation import ugettext as _

from .signals import *  # NOQA

ORDER_STATUS_PLACED = 0
ORDER_STATUS_DENIED = 1
ORDER_STATUS_RECEIVED = 2
ORDER_STATUS_STARTED = 3
ORDER_STATUS_WAITING = 4
ORDER_STATUS_COMPLETED = 5
ORDER_STATUS_NOT_COLLECTED = 6
ORDER_STATUSES = (
    (ORDER_STATUS_PLACED, _('Geplaatst'), order_created),
    (ORDER_STATUS_DENIED, _('Afgewezen'), order_denied),
    (ORDER_STATUS_RECEIVED, _('Ontvangen'), order_received),
    (ORDER_STATUS_STARTED, _('Aan begonnen'), order_started),
    (ORDER_STATUS_WAITING, _('Ligt klaar'), order_waiting),
    (ORDER_STATUS_COMPLETED, _('Voltooid'), order_completed),
    (ORDER_STATUS_NOT_COLLECTED, _('Niet opgehaald'), order_not_collected)
)

GROUP_ORDER_STATUSES = (
    (ORDER_STATUS_PLACED, _('Geplaatst'), group_order_created),
    (ORDER_STATUS_DENIED, _('Afgewezen'), group_order_denied),
    (ORDER_STATUS_RECEIVED, _('Ontvangen'), group_order_received),
    (ORDER_STATUS_STARTED, _('Aan begonnen'), group_order_started),
    (ORDER_STATUS_WAITING, _('Ligt klaar'), group_order_waiting),
    (ORDER_STATUS_COMPLETED, _('Voltooid'), group_order_completed),
    (ORDER_STATUS_NOT_COLLECTED, _('Niet opgehaald'), group_order_not_collected)
)
ORDER_STATUSES_ENDED = [
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_DENIED,
    ORDER_STATUS_NOT_COLLECTED
]
ORDER_STATUSES_ACTIVE = [
    ORDER_STATUS_PLACED,
    ORDER_STATUS_RECEIVED,
    ORDER_STATUS_STARTED,
    ORDER_STATUS_WAITING
]

ORDEREDFOOD_STATUS_OK = 0
ORDEREDFOOD_STATUS_OUT_OF_STOCK = 1
ORDEREDFOOD_STATUSES = (
    (ORDEREDFOOD_STATUS_OK, _('Oké'), orderedfood_created),
    (ORDEREDFOOD_STATUS_OUT_OF_STOCK, _('Uit voorraad'), orderedfood_out_of_stock),
)

DEMO_PHONE = '+32411111111'

PAYMENT_METHOD_CASH = 0
PAYMENT_METHOD_GOCARDLESS = 1
PAYMENT_METHOD_PAYCONIQ = 2

PAYMENT_METHODS = (
    (PAYMENT_METHOD_CASH, _('Betalen in winkel')),
    (PAYMENT_METHOD_GOCARDLESS, _('Online (veilig via GoCardless)')),
    (PAYMENT_METHOD_PAYCONIQ, _('Online (veilig via Payconiq)')),
)

PAYMENTLINK_COMPLETION_REDIRECT_URL = 'lunchbreak://gocardless/redirectflow/'
