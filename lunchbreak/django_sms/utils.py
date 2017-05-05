import base64
import hmac
from hashlib import sha1


def validate_plivo_signature(signature, post_params, webhook_url, auth_token):
    if isinstance(auth_token, str):
        auth_token = auth_token.encode('utf-8')

    encoded_request = webhook_url
    if isinstance(encoded_request, str):
        encoded_request = encoded_request.encode('utf-8')

    if isinstance(signature, str):
        signature = signature.encode('utf-8')

    for key, value in sorted(post_params.items()):
        encoded_key = key.encode('utf-8')
        if isinstance(value, str):
            encoded_val = value.encode('utf-8')
        else:
            encoded_val = '' if value is None else str(value)
        encoded_request += encoded_key + encoded_val

    generated_signature = base64.encodestring(
        hmac.new(
            auth_token,
            encoded_request,
            sha1
        ).digest()
    ).strip()

    return generated_signature == signature
