import os

BRANCH = 'development'
PORT = '8002'

SSL = False
DEBUG = True

PRIVATE_MEDIA_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'media-private'))

MIDDLEWARE_CLASSES += (
    'lunch.middleware.PrintExceptionMiddleware',
    'qinspect.middleware.QueryInspectMiddleware',
)

BUSINESS_APNS_CERTIFICATE = '../salt/synced/salt/keys/apns/business_development.pem'
CUSTOMERS_APNS_CERTIFICATE = '../salt/synced/salt/keys/apns/customers_development.pem'

QUERY_INSPECT_ENABLED = True
#QUERY_INSPECT_LOG_QUERIES = True
QUERY_INSPECT_LOG_TRACEBACKS = True
