from .models import GroupOrder, Order
from .signals import *  # NOQA

order_created.connect(
    Order.created,
    dispatch_uid='customers_order_created'
)
order_waiting.connect(
    Order.waiting,
    dispatch_uid='customers_order_waiting'
)
order_completed.connect(
    Order.denied,
    dispatch_uid='customers_order_completed'
)
order_denied.connect(
    Order.denied,
    dispatch_uid='customers_order_denied'
)
order_not_collected.connect(
    Order.denied,
    dispatch_uid='customers_order_not_collected'
)

group_order_created.connect(
    GroupOrder.created,
    dispatch_uid='customers_group_order_created'
)
