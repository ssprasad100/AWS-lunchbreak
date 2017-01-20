GOCARDLESS_ENVIRONMENT = 'sandbox'
GOCARDLESS_APP_DOMAIN = 'api.andreas.cloock.be'
MIDDLEWARE_CLASSES += (
    'lunch.middleware.PrintExceptionMiddleware',
    'qinspect.middleware.QueryInspectMiddleware',
    'livereload.middleware.LiveReloadScript',
)

ALLOWED_HOSTS = [
    'lunchbreak.dev',
    'www.lunchbreak.dev',
    'api.lunchbreak.dev',

    'andreas.cloock.be',
    'www.andreas.cloock.be',
    'api.andreas.cloock.be',
]

INSTALLED_APPS = [
    'livereload',
    'django_extensions',
] + INSTALLED_APPS

SSL = False
DEBUG = True

QUERY_INSPECT_ENABLED = True
#QUERY_INSPECT_LOG_QUERIES = True
QUERY_INSPECT_LOG_TRACEBACKS = True

APNS_HOST = 'gateway.sandbox.push.apple.com'
APNS_FEEDBACK_HOST = 'feedback.sandbox.push.apple.com'
AMQP_USER = 'guest'
AMQP_PASSWORD = 'guest'
AMQP_HOST = '127.0.0.1'
