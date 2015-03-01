=====
Token
=====

Token list
==========

.. http:get:: /v1/customers/token/

    List token for authenticated user.

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed

    :resjsonarr int id: token ID
    :resjsonarr string device: device name
    :resjsonarr string identifier: identifier used in headers
    :resjsonarr string name: user's name
    :resjsonarr int user_id: user ID
