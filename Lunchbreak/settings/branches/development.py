import os

BRANCH = 'development'
PORT = '8002'

SSL = False
DEBUG = True

PRIVATE_MEDIA_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'media-private'))
