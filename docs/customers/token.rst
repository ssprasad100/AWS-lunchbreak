=====
Token
=====

Token list
==========

.. http:get:: /v1/customers/token/

    List token for authenticated user.

    Serializer: :doc:`/serializers/customers/userToken`

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed
