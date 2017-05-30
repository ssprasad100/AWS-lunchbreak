from django.conf import settings

from .resources import *  # noqa

version = (0, 1, 0)
extra = ''
__version__ = '.'.join(map(str, version)) + extra

__author__ = 'Andreas Backx'
__email__ = 'andreas@backx.org'
__license__ = 'MIT'

merchant_id = None
merchant_token = None

api_base = 'https://api.payconiq.com/v2'
api_base_test = 'https://dev.payconiq.com/v2'

default_app_config = 'payconiq.apps.PayconiqAppConfig'

public_key_production = b'''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA7c+Bl6e/jUBTn/QsNMeD
jyvrI8iZl3koxNohCwe0HnP/l1NhYtzAPuCoPd3NLt7ttjicIaG51n3hoZFrNSPD
ZD1O5KG9wlbh5X4potUyEHeRHynCfJggNyrJC2/77ZRcBhZllsjCzQUSk0iDIdbW
ISQrAvYqHLTF4Ckk+c29CRavbN6jWPS1otxkkCdITrw+iIi+Msr3AkUC0EAxwDrT
sLAypN35v6jOxyTfzO5h+upypGWH+gCqJ3jxOrgP90a7ylUXO2BTKktoS/9C9v8h
/7hyhgr9bVU+yYtmb9xP9s7RBOz8tQYS2HGkoM1hKCDuWUEbEdK3AdJQCBDzRF3z
OQIDAQAB
-----END PUBLIC KEY-----'''

public_key_testing = b'''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtxS9KJhwYLQ88Y5B5ZRL
QHuJLAbYUBk6aFKeTZvLLTYd+ptfcVzoL6tnF4TV1D/0kkweoVk5WuQEbL5kP9H4
hqPUlg7anI4B6PZTQ37FysCmvPoxjJLKT7LQ0lDD9qGV7IbYZZ0Oep3Sp3i0chrn
2ec4KpkTl1bbEueItMaJGZMJjQhDg6sOXPOFewn/OvttRzTSLkhzIQEbmcJXpk7L
wf/u5dyM0Rx0cNJQZgmPDhqRKbRv7CtLt06rK78RRLAfZmwknP7pIV7MHtlX4yzk
FDf1Ig/onw8x+ej/yb/IOed5BQkiyuwS0lCWnywncA1eVNcCI7o9OuJsiIklL5ku
DwIDAQAB
-----END PUBLIC KEY-----'''


def get_payconiq_settings():
    return getattr(settings, 'PAYCONIQ', {})


def get_base_url():
    return api_base \
        if get_payconiq_settings().get('environment', 'testing') == 'production' \
        else api_base_test


def get_webhook_domain():
    return get_payconiq_settings().get('webhook_domain')


def get_api_base():
    return payconiq.api_base \
        if get_payconiq_settings().get('environment', 'testing') == 'production' \
        else payconiq.api_base_test


def get_public_key():
    return public_key_production \
        if get_payconiq_settings().get('environment', 'testing') == 'production' \
        else public_key_testing
