import os

BRANCH = 'development'
PORT = '8002'

SSL = False
DEBUG = True

PRIVATE_MEDIA_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'media-private'))

MIDDLEWARE_CLASSES += (
    'qinspect.middleware.QueryInspectMiddleware',
)

QUERY_INSPECT_ENABLED = True
#QUERY_INSPECT_LOG_QUERIES = True
QUERY_INSPECT_LOG_TRACEBACKS = True
