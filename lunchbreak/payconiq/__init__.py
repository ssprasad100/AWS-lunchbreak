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
environment = 'production'

from .resources import *  # noqa


default_app_config = 'payconiq.apps.PayconiqAppConfig'


def get_base_url():
    return api_base if environment == 'production' else api_base_test
