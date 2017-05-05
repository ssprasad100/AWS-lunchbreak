GOCARDLESS_ENVIRONMENT = 'sandbox'
GOCARDLESS_APP_DOMAIN = 'api.andreas.cloock.be'

PLIVO_WEBHOOK_URL = 'http://api.andreas.cloock.be/sms/plivo'
TWILIO_WEBHOOK_URL = 'http://api.andreas.cloock.be/sms/twilio'

MIDDLEWARE_CLASSES += (
    'lunch.middleware.PrintExceptionMiddleware',
    'qinspect.middleware.QueryInspectMiddleware',
    'livereload.middleware.LiveReloadScript',
)

ALLOWED_HOSTS = [
    'lunchbreak.dev',
    'www.lunchbreak.dev',
    'api.lunchbreak.dev',

    'lunchbreak.redirect',
    'www.lunchbreak.redirect',
    'api.lunchbreak.redirect',

    'andreas.cloock.be',
    'www.andreas.cloock.be',
    'api.andreas.cloock.be',
]

REDIRECTED_HOSTS = {
    'lunchbreak.redirect': 'www.lunchbreak.dev',
    'www.lunchbreak.redirect': 'www.lunchbreak.dev',
}

INSTALLED_APPS = [
    'livereload',
    'django_extensions',
] + INSTALLED_APPS

SSL = False
DEBUG = True

QUERY_INSPECT_LOG_TRACEBACKS = False

# Whether the Query Inspector should do anything (default: False)
QUERY_INSPECT_ENABLED = True
# Whether to log the stats via Django logging (default: True)
QUERY_INSPECT_LOG_STATS = True
# Whether to add stats headers (default: True)
QUERY_INSPECT_HEADER_STATS = True
# Whether to log duplicate queries (default: False)
QUERY_INSPECT_LOG_QUERIES = True
# Whether to log queries that are above an absolute limit (default: None - disabled)
QUERY_INSPECT_ABSOLUTE_LIMIT = None # in milliseconds
# Whether to log queries that are more than X standard deviations above the mean query time (default: None - disabled)
QUERY_INSPECT_STANDARD_DEVIATION_LIMIT = None
# Whether to include tracebacks in the logs (default: False)
QUERY_INSPECT_LOG_TRACEBACKS = False
# Project root (a list of directories, see below - default empty)
QUERY_INSPECT_TRACEBACK_ROOTS = ['/Users/Andreas/Development/Python/Lunchbreak-Backend']

APNS_HOST = 'gateway.sandbox.push.apple.com'
APNS_FEEDBACK_HOST = 'feedback.sandbox.push.apple.com'
AMQP_USER = 'guest'
AMQP_PASSWORD = 'guest'
AMQP_HOST = '127.0.0.1'
