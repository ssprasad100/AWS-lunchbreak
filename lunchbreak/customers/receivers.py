from .models import Order
from .signals import *  # NOQA

order_created.connect(
    Order.created,
    dispatch_uid='customers_order_created'
)
order_waiting.connect(
    Order.waiting,
    dispatch_uid='customers_order_waiting'
)
order_denied.connect(
    Order.denied,
    dispatch_uid='customers_order_denied'
)