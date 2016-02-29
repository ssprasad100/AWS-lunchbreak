import base64
import json
import urllib

import requests
from customers.exceptions import DigitsException
from Lunchbreak.exceptions import LunchbreakException


class Digits:
    CONSUMER_KEY = 'EF63FOnX3hZ1Ry7lRUXhJtAkr'
    CONSUMER_SECRET = 'aIKxPtKqKD1G2NisdKCACzPlEEMi2Jyg4xQH6pzlEjxiCXIRob'

    BASE_URL = 'https://api.twitter.com/'
    REGISTER_URL = BASE_URL + '1.1/device/register.json'
    ACCOUNT_URL = BASE_URL + '1.1/sdk/account.json'
    XAUTH_PHONE_URL = BASE_URL + 'auth/1/xauth_phone_number.json'
    XAUTH_CHALLENGE_URL = BASE_URL + 'auth/1/xauth_challenge.json'
    GUEST_TOKEN_URL = BASE_URL + '1.1/guest/activate.json'
    ACCESS_TOKEN_URL = BASE_URL + 'oauth2/token'

    @property
    def header_bearer(self):
        return 'Bearer ' + self.app_token()

    @property
    def header_auth(self):
        return 'Basic {base}'.format(
            base=base64.b64encode(
                urllib.quote(Digits.CONSUMER_KEY) +
                ':' +
                urllib.quote(Digits.CONSUMER_SECRET)
            )
        )

    @property
    def app_token(self):
        """
        An app token or bearer token is needed in order to talk to the OAuth
        API of Twitter.
        """

        if not hasattr(self, '_app_token'):
            params = {
                'grant_type': 'client_credentials'
            }

            headers = {
                'Authorization': self.header_auth
            }

            content = self.request(
                Digits.ACCESS_TOKEN_URL,
                params=params,
                headers=headers
            )

            self._app_token = content['access_token']
        return self._app_token

    @property
    def guest_token(self):
        """
        A guest token is needed in order to talk to the Digits API of Twitter
        before sending text messages.
        """

        params = {
            'grant_type': 'client_credentials'
        }

        headers = {
            'Authorization': self.header_bearer
        }

        content = self.request(
            Digits.GUEST_TOKEN_URL,
            params=params,
            headers=headers
        )

        return content['guest_token']

    def request(self, url, params, headers):
        """
        A wrapper method for send POST requests.
        """

        response = requests.post(
            url,
            params=params,
            headers=headers
        )

        content = json.loads(response.text)

        if response.status_code != 200:
            if 'errors' in content and 'code' in content['errors'][0]:
                raise DigitsException(content['errors'][0]['code'], content)
            raise LunchbreakException(content)

        return content

    def register(self, phone_number):
        """
        Register a user in the Digits database. They will receive a text
        message to confirm that they're the true owner of the given phone number.

        Return example:
        {
            "phone_number": "+32479427866",
            "opt_in_method_used": null,
            "registration_id": null,
            "user_id": null,
            "state": "AwaitingComplete",
            "reference_id": null,
            "error": null,
            "is_verizon": false,
            "device_id": 1432136745
        }
        """

        params = {
            'raw_phone_number': phone_number,
            'text_key': 'third_party_confirmation_code',
            'send_numeric_pin': True
        }

        headers = {
            'Authorization': self.header_bearer,
            'x-guest-token': self.guest_token
        }

        content = self.request(
            Digits.REGISTER_URL,
            params=params,
            headers=headers
        )

        return content

    def register_confirm(self, phone_number, pin):
        """
        Check whether the sent pin is correct.

        Return example:
        {
            "created_at": "Sun Nov 23 16:44:40 +0000 2014",
            "needs_phone_verification": false,
            "id": 2889428578,
            "suspended": false,
            "id_str": "2889428578"
        }
        """

        params = {
            'phone_number': phone_number,
            'numeric_pin': pin
        }

        headers = {
            'Authorization': self.header_bearer
        }

        content = self.request(
            Digits.ACCOUNT_URL,
            params,
            headers
        )

        return content

    def signin(self, phone_number):
        """
        Send the already registered user in if they don't have their token anymore.

        Return example:
        {
            "login_verification_request_cause": 3,
            "login_verification_request_id": String,
            "login_verification_user_id": long,
            "login_verification_request_url": String,
            "login_verification_request_type": int
        }
        """
        params = {
            'x_auth_phone_number': phone_number
        }

        headers = {
            'Authorization': self.header_bearer,
            'x-guest-token': self.guest_token
        }

        content = self.request(
            Digits.XAUTH_PHONE_URL,
            params=params,
            headers=headers
        )

        return content

    def signing_confirm(self, request_id, user_id, pin):
        """
        Confirm that the pin the user sent is correct.

        Return example:
        {
            'oauth_token_secret': 'nBeRqRbZXeiqPq5px8c7bH2To2g9BUC6c6bt25GFacQNU',
            'user_id': 2866750414,
            'x_auth_expires': 0,
            'oauth_token': '2866750414-Hb5OdbmPwQWfU2LYtqKKY4t1rdhmj1xVjuAxEvv',
            'screen_name': ''
        }
        """

        params = {
            'login_verification_request_id': request_id,
            'login_verification_user_id': user_id,
            'login_verification_challenge_response': pin
        }

        headers = {
            'Authorization': self.header_bearer,
            'x-guest-token': self.guest_token
        }

        content = self.request(
            Digits.XAUTH_CHALLENGE_URL,
            params,
            headers
        )

        return content
