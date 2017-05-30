from base64 import b64decode, b64encode
from binascii import Error, crc32
from hashlib import sha256

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends.openssl import backend as openssl_backend
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA256
from django.conf import settings
from payconiq import get_public_key

from .exceptions import PayconiqError


def is_signature_valid(signature, merchant_id, timestamp, algorithm, body):
    if isinstance(signature, str):
        signature = signature.encode('utf8')

    if isinstance(body, str):
        body = body.encode('utf8')

    if algorithm == 'SHA256WithRSA':
        crc32_decimal = crc32(body)
        crc32_hex = hex(crc32_decimal)[2:]
        try:
            signature_decoded = b64decode(signature)
        except Error:
            return False

        formatted_signature = '{merchant_id}|{timestamp}|{crc32}'.format(
            merchant_id=merchant_id,
            timestamp=timestamp,
            crc32=crc32_hex
        ).encode('utf8')

        try:
            public_key = openssl_backend.load_pem_public_key(
                data=get_public_key()
            )
        except ValueError as e:
            raise PayconiqError(str(e))

        try:
            public_key.verify(
                signature_decoded,
                formatted_signature,
                PKCS1v15(),
                SHA256()
            )
            return True
        except InvalidSignature:
            pass
    return False


def generate_web_signature(merchant_id, webhook_id, currency, amount, widget_token):
    formatted_signature = '{merchant_id}{webhook_id}{currency}{amount}{widget_token}'.format(
        merchant_id=merchant_id,
        webhook_id=webhook_id,
        currency=currency,
        amount=amount,
        widget_token=widget_token
    ).encode('utf8')

    signature = sha256()
    signature.update(formatted_signature)

    return b64encode(
        signature.digest()
    ).decode('utf-8')


def get_widget_url():
    return 'https://{subdomain}.payconiq.com/v2/online/static/widget.js'.format(
        subdomain='api' if getattr(settings, 'PAYCONIQ_ENVIRONMENT',
                                   'testing') == 'production' else 'dev'
    )
    return 'https://api.payconiq.com/v2/online/static/widget.js' \
        if getattr(settings, 'PAYCONIQ_ENVIRONMENT', 'testing') == 'production' \
        else 'https://dev.payconiq.com/v2/online/static/widget.js'
