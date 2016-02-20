ORDER_STATUS_PLACED = 0
ORDER_STATUS_DENIED = 1
ORDER_STATUS_RECEIVED = 2
ORDER_STATUS_STARTED = 3
ORDER_STATUS_WAITING = 4
ORDER_STATUS_COMPLETED = 5
ORDER_STATUS_NOT_COLLECTED = 6

ORDER_STATUS = (
    (ORDER_STATUS_PLACED, 'Placed'),
    (ORDER_STATUS_DENIED, 'Denied'),
    (ORDER_STATUS_RECEIVED, 'Received'),
    (ORDER_STATUS_STARTED, 'Started'),
    (ORDER_STATUS_WAITING, 'Waiting'),
    (ORDER_STATUS_COMPLETED, 'Completed'),
    (ORDER_STATUS_NOT_COLLECTED, 'Not collected')
)

ORDER_ENDED = [
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_DENIED,
    ORDER_STATUS_NOT_COLLECTED
]

RESERVATION_STATUS_PLACED = 0
RESERVATION_STATUS_DENIED = 1
RESERVATION_STATUS_ACCEPTED = 2
RESERVATION_STATUS_CANCELLED = 3
RESERVATION_STATUS_COMPLETED = 4
RESERVATION_STATUS_NO_SHOW = 5

RESERVATION_STATUS = (
    (ORDER_STATUS_PLACED, 'Placed'),
    (RESERVATION_STATUS_DENIED, 'Denied'),
    (RESERVATION_STATUS_ACCEPTED, 'Accepted'),
    (RESERVATION_STATUS_CANCELLED, 'Cancelled'),
    (RESERVATION_STATUS_COMPLETED, 'Completed'),
    (RESERVATION_STATUS_NO_SHOW, 'No show'),
)

RESERVATION_STATUS_USER_CHANGE = (
    (ORDER_STATUS_PLACED, 'Placed'),
    (RESERVATION_STATUS_ACCEPTED, 'Accepted'),
)

RESERVATION_STATUS_USER = (
    (RESERVATION_STATUS_CANCELLED, 'Cancelled'),
)

RESERVATION_STATUS_EMPLOYEE = (
    (RESERVATION_STATUS_DENIED, 'Denied'),
    (RESERVATION_STATUS_ACCEPTED, 'Accepted'),
    (RESERVATION_STATUS_COMPLETED, 'Completed'),
    (RESERVATION_STATUS_NO_SHOW, 'No show'),
)

DEMO_PHONE = '+32411111111'
DEMO_DIGITS_ID = 'demo'