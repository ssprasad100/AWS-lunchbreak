=====
Token
=====

Token list
==========

.. http:get:: /v1/customers/token/

    List token for authenticated user.

    :>header X-Identifier: Identifier token of the UserToken
    :>header X-User: ID of the user
    :>header X-Device: Name of the device

    :<header Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed
