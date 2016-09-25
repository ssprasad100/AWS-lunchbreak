from django.conf import settings

CLIENT_PROPERTIES = {
    'Customer': 'customers',
    'CustomerBankAccount': 'customer_bank_accounts',
    'Mandate': 'mandates',
    'RedirectFlow': 'redirect_flows',
    'Payout': 'payouts',
    'Subscription': 'subscriptions',
    'Payment': 'payments',
    'Refund': 'refunds',
}

SCHEMES = (
    ('autogiro', 'Autogiro',),
    ('bacs', 'Bacs',),
    ('sepa_core', 'Sepa Core',),
    ('sepa_cor1', 'Sepa Cor1',),
)

CURRENCY_EUR = 'EUR'
CURRENCY_GBP = 'GBP'
CURRENCY_SEK = 'SEK'
CURRENCIES = (
    ('EUR', 'Euro'),
    ('GBP', 'British Pound'),
    ('SEK', 'Swedish Krona'),
)

MANDATE_STATUSES = (
    ('pending_submission', 'Pending submission',),
    ('submitted', 'Submitted',),
    ('active', 'Active',),
    ('failed', 'Failed',),
    ('cancelled', 'Cancelled',),
    ('expired', 'Expired',),
)

PAYMENT_STATUSES = (
    ('pending_submission', 'Pending submission'),
    ('submitted', 'Submitted'),
    ('confirmed', 'Confirmed'),
    ('failed', 'Failed'),
    ('charged_back', 'Charged back'),
    ('paid_out', 'Paid out'),
    ('cancelled', 'Cancelled'),
    ('pending_customer_approval', 'Pending customer approval'),
    ('customer_approval_denied', 'Customer approval denied'),
)

SUBSCRIPTION_DAY_OF_MONTH = (
    (-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'),
    (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12'),
    (13, '13'), (14, '14'), (15, '15'), (16, '16'), (17, '17'), (18, '18'),
    (19, '19'), (20, '20'), (21, '21'), (22, '22'), (23, '23'), (24, '24'),
    (25, '25'), (26, '26'), (27, '27'), (28, '28'),
)

SUBSCRIPTION_INTERVAL_UNIT = (
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('yearly', 'Yearly'),
)

SUBSCRIPTION_MONTHS = (
    ('january', 'January'),
    ('february', 'February'),
    ('march', 'March'),
    ('april', 'April'),
    ('may', 'May'),
    ('june', 'June'),
    ('july', 'July'),
    ('august', 'August'),
    ('september', 'September'),
    ('october', 'October'),
    ('november', 'November'),
    ('december', 'December')
)

SUBSCRIPTION_STATUSES = (
    ('pending_customer_approval', 'Pending customer approval'),
    ('customer_approval_denied', 'Customer approval denied'),
    ('active', 'Active'),
    ('finished', 'Finished'),
    ('cancelled', 'Cancelled'),
)

PAYOUT_STATUSES = (
    ('pending', 'Pending'),
    ('paid', 'Paid'),
)

DEFAULT_DOMAIN = settings.GOCARDLESS.get(
    'default_domain',
    settings.ALLOWED_HOSTS[0]
)
