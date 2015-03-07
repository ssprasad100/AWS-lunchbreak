====
User
====

Registration
============

.. http:post:: /v1/customers/user/

    Register the user's phone number.

    Serializer: :doc:`/serializers/customers/user`

    :reqheader Content-Type: application/json

    :form phone: user phone number

    :resheader Content-Type: application/json

    :status 200: message has been sent
    :status 201: user has been added (needs name) to the database and a message has been sent
    :status 400: form parameters missing

Confirmation
============

.. http:post:: /v1/customers/user/

    Confirm a user's registration.

    Request serializer: :doc:`/serializers/customers/user`

    Response serializer: :doc:`/serializers/customers/userToken`

    :reqheader Content-Type: application/json

    :form phone: user phone number
    :form device: device name
    :form pin: pin code received
    :form name: optional name if user's name is not in database

    :resheader Content-Type: application/json

    :status 200: token with device exists, new identifier generated
    :status 201: token has been added
    :status 400: form parameters missing
