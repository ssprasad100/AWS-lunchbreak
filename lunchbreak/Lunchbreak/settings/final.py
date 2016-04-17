import os

if 'ALLOWED_HOSTS' not in globals():
    ALLOWED_HOSTS = []

if HOST not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(HOST)

DB_NAME = DB_NAME if 'DB_NAME' in globals() else 'LB_%s' % BRANCH
DB_USER = DB_USER if 'DB_USER' in globals() else DB_NAME

if 'DB_PASS' not in globals():
    DB_PASS = os.environ.get('MYSQL_PASSWORD')
DB_PASS = DB_PASS if DB_PASS is not None else DB_NAME

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': 'localhost',
        'PORT': '3306'
    }
}

OPBEAT_RELEASE = OPBEAT_RELEASE if 'OPBEAT_RELEASE' in globals() else False

GOOGLE_CLOUD_SECRET = GOOGLE_CLOUD_SECRET if 'GOOGLE_CLOUD_SECRET' in globals(
) else os.environ.get('GOOGLE_CLOUD_SECRET')

BUSINESS_APNS_CERTIFICATE = BUSINESS_APNS_CERTIFICATE if 'BUSINESS_APNS_CERTIFICATE' in globals(
) else os.environ.get('BUSINESS_APNS_CERTIFICATE', 'certificates/apns/business_development.pem')
CUSTOMERS_APNS_CERTIFICATE = CUSTOMERS_APNS_CERTIFICATE if 'CUSTOMERS_APNS_CERTIFICATE' in globals(
) else os.environ.get('CUSTOMERS_APNS_CERTIFICATE', 'certificates/apns/customers_development.pem')

PUSH_NOTIFICATIONS_SETTINGS = {
    'GCM_API_KEY': GOOGLE_CLOUD_SECRET,
    'APNS_CERTIFICATE': CUSTOMERS_APNS_CERTIFICATE,
}
