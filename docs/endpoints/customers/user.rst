====
User
====

Registration
============

.. http:post:: /v1/customers/user/

    Register the user's phone number.

    Serializer: :doc:`/serializers/customers/user`

    :reqjson phone: user phone number

    :status 200: message has been sent
    :status 201: user has been added (needs name) to the database and a message has been sent

Confirmation
============

.. http:post:: /v1/customers/user/

    Confirm a user's registration.

    Request serializer: :doc:`/serializers/customers/user`

    Response serializer: :doc:`/serializers/customers/userToken`

    :reqjson phone: user phone number
    :reqjson device: device name
    :reqjson pin: pin code received
    :reqjson name: optional name if user's name is not in database

    :status 200: token with device exists, new identifier generated
    :status 201: token has been added
