ALLOWED_HOSTS = [
    'lunchbreak.dev',
    'www.lunchbreak.dev',
    'api.lunchbreak.dev',

    'andreas.cloock.be',
    'www.andreas.cloock.be',
    'api.andreas.cloock.be',
]
BRANCH = 'development'

SSL = False
DEBUG = True

INSTALLED_APPS = [
    'livereload',
] + INSTALLED_APPS

MIDDLEWARE_CLASSES += (
    'lunch.middleware.PrintExceptionMiddleware',
    'qinspect.middleware.QueryInspectMiddleware',
    'livereload.middleware.LiveReloadScript',
)

APNS_HOST = 'gateway.sandbox.push.apple.com'
APNS_FEEDBACK_HOST = 'feedback.sandbox.push.apple.com'

QUERY_INSPECT_ENABLED = True
#QUERY_INSPECT_LOG_QUERIES = True
QUERY_INSPECT_LOG_TRACEBACKS = True

TEMPLATES[0]['OPTIONS']['constants']['dir'] = 'dir'
GOCARDLESS_ENVIRONMENT = 'sandbox'
GOCARDLESS_APP_EXCHANGE_DOMAIN = 'api.andreas.cloock.be'
