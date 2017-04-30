from base64 import b64decode
from binascii import Error, crc32

import payconiq
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends.openssl import backend as openssl_backend
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA256

from .exceptions import PayconiqError


def get_api_base():
    return payconiq.api_base \
        if payconiq.environment == 'production' else payconiq.api_base_test


public_pem_data = b'''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtxS9KJhwYLQ88Y5B5ZRL
QHuJLAbYUBk6aFKeTZvLLTYd+ptfcVzoL6tnF4TV1D/0kkweoVk5WuQEbL5kP9H4
hqPUlg7anI4B6PZTQ37FysCmvPoxjJLKT7LQ0lDD9qGV7IbYZZ0Oep3Sp3i0chrn
2ec4KpkTl1bbEueItMaJGZMJjQhDg6sOXPOFewn/OvttRzTSLkhzIQEbmcJXpk7L
wf/u5dyM0Rx0cNJQZgmPDhqRKbRv7CtLt06rK78RRLAfZmwknP7pIV7MHtlX4yzk
FDf1Ig/onw8x+ej/yb/IOed5BQkiyuwS0lCWnywncA1eVNcCI7o9OuJsiIklL5ku
DwIDAQAB
-----END PUBLIC KEY-----'''


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
                data=public_pem_data
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
