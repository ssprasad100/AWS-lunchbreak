=====
Token
=====

Token list
==========

.. http:get:: /v1/customers/token/

    List token for authenticated user.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/customers/userToken`

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed
