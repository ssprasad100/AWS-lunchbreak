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
    def bearerHeader(self):
        return 'Bearer ' + self.requestAppToken()

    @property
    def authHeader(self):
        return 'Basic {base}'.format(
            base=base64.b64encode(
                urllib.quote(Digits.CONSUMER_KEY) +
                ':' +
                urllib.quote(Digits.CONSUMER_SECRET)
            )
        )

    def request(self, url, params, headers):
        '''A wrapper method for send POST requests.'''

        appTokenRequest = requests.post(
            url,
            params=params,
            headers=headers
        )

        content = json.loads(appTokenRequest.text)

        if appTokenRequest.status_code != 200:
            if 'errors' in content and 'code' in content['errors'][0]:
                raise DigitsException(content['errors'][0]['code'], content)
            raise LunchbreakException(content)

        return content

    def requestAppToken(self):
        '''An app token or bearer token is needed in order to talk to the OAuth API of Twitter.'''

        if not hasattr(self, 'appToken'):
            params = {
                'grant_type': 'client_credentials'
            }

            headers = {
                'Authorization': self.authHeader
            }

            content = self.request(
                Digits.ACCESS_TOKEN_URL,
                params=params,
                headers=headers
            )

            self.appToken = content['access_token']
        return self.appToken

    def requestGuestToken(self):
        '''A guest token is needed in order to talk to the Digits API of Twitter before sending text messages.'''

        params = {
            'grant_type': 'client_credentials'
        }

        headers = {
            'Authorization': self.bearerHeader
        }

        content = self.request(
            Digits.GUEST_TOKEN_URL,
            params=params,
            headers=headers
        )

        return content['guest_token']

    def register(self, phoneNumber):
        '''Register a user in the Digits database. They will receive a text message to confirm that they're the true owner of the given phone number.

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
        '''

        params = {
            'raw_phone_number': phoneNumber,
            'text_key': 'third_party_confirmation_code',
            'send_numeric_pin': True
        }

        headers = {
            'Authorization': self.bearerHeader,
            'x-guest-token': self.requestGuestToken()
        }

        content = self.request(
            Digits.REGISTER_URL,
            params=params,
            headers=headers
        )

        return content

    def confirmRegistration(self, phoneNumber, pin):
        '''Check whether the sent pin is correct.

        Return example:
        {
            "created_at": "Sun Nov 23 16:44:40 +0000 2014",
            "needs_phone_verification": false,
            "id": 2889428578,
            "suspended": false,
            "id_str": "2889428578"
        }
        '''

        params = {
            'phone_number': phoneNumber,
            'numeric_pin': pin
        }

        headers = {
            'Authorization': self.bearerHeader
        }

        content = self.request(
            Digits.ACCOUNT_URL,
            params,
            headers
        )

        return content

    def signin(self, phoneNumber):
        '''Send the already registered user in if they don't have their token anymore.

        Return example:
        {
            "login_verification_request_cause": 3,
            "login_verification_request_id": String,
            "login_verification_user_id": long,
            "login_verification_request_url": String,
            "login_verification_request_type": int
        }
        '''
        params = {
            'x_auth_phone_number': phoneNumber
        }

        headers = {
            'Authorization': self.bearerHeader,
            'x-guest-token': self.requestGuestToken()
        }

        content = self.request(
            Digits.XAUTH_PHONE_URL,
            params=params,
            headers=headers
        )

        return content

    def confirmSignin(self, requestId, userId, pin):
        '''Confirm that the pin the user sent is correct.

        Return example:
        {
            'oauth_token_secret': 'nBeRqRbZXeiqPq5px8c7bH2To2g9BUC6c6bt25GFacQNU',
            'user_id': 2866750414,
            'x_auth_expires': 0,
            'oauth_token': '2866750414-Hb5OdbmPwQWfU2LYtqKKY4t1rdhmj1xVjuAxEvv',
            'screen_name': ''
        }
        '''

        params = {
            'login_verification_request_id': requestId,
            'login_verification_user_id': userId,
            'login_verification_challenge_response': pin
        }

        headers = {
            'Authorization': self.bearerHeader,
            'x-guest-token': self.requestGuestToken()
        }

        content = self.request(
            Digits.XAUTH_CHALLENGE_URL,
            params,
            headers
        )

        return content
