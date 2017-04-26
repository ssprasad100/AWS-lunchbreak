from django.db.models.signals import post_delete, post_save
from payconiq.signals import *  # NOQA

from .models import Group, GroupOrder, Order, OrderedFood, PaymentLink
from .signals import *  # NOQA

post_delete.connect(
    PaymentLink.post_delete,
    sender=PaymentLink,
    weak=False
)

post_save.connect(
    OrderedFood.post_save,
    sender=OrderedFood,
    weak=False
)

order_created.connect(
    Order.created,
    dispatch_uid='customers_order_created'
)
order_waiting.connect(
    Order.waiting,
    dispatch_uid='customers_order_waiting'
)
order_completed.connect(
    Order.completed,
    dispatch_uid='customers_order_completed'
)
order_denied.connect(
    Order.denied,
    dispatch_uid='customers_order_denied'
)
order_not_collected.connect(
    Order.not_collected,
    dispatch_uid='customers_order_not_collected'
)

group_order_created.connect(
    GroupOrder.created,
    dispatch_uid='customers_group_order_created'
)

post_save.connect(
    Group.post_save,
    sender=Group,
    weak=False
)

transaction_timedout.connect(
    Order.transaction_timedout,
    dispatch_uid='customers_transaction_timedout'
)
transaction_canceled.connect(
    Order.transaction_canceled,
    dispatch_uid='customers_transaction_canceled'
)
transaction_failed.connect(
    Order.transaction_failed,
    dispatch_uid='customers_transaction_failed'
)
transaction_succeeded.connect(
    Order.transaction_succeeded,
    dispatch_uid='customers_transaction_succeeded'
)
