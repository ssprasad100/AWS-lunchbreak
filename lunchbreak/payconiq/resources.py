import payconiq
import requests

from .exceptions import PayconiqError


class Transaction:

    @classmethod
    def get_base_url(cls):
        payconiq.environment = 'testing'
        return '{base_url}/transactions'.format(
            base_url=payconiq.get_base_url()
        )

    @classmethod
    def request(cls, *args, **kwargs):
        response = requests.request(*args, **kwargs)
        if not 199 < response.status_code < 300:
            raise PayconiqError.from_response(
                response=response
            )
        return response

    @classmethod
    def start(cls, amount, webhook_url, currency='EUR', merchant_token=None):
        merchant_token = merchant_token \
            if merchant_token is not None else payconiq.merchant_token

        response = cls.request(
            method='POST',
            url=cls.get_base_url(),
            headers={
                'Authorization': merchant_token,
            },
            json={
                'amount': amount,
                'currency': currency,
                'callback_url': webhook_url,
            }
        )
        return response.json()['transactionId']
