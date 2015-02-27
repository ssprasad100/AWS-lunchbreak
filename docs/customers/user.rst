====
User
====

Registration
============

.. http:post:: /v1/customers/user/

    Register the user's phone number.

    :form phone: user phone number

    :>header Content-Type: application/x-www-form-urlencoded
    :<header Content-Type: application/json

    :status 200: message has been sent
    :status 201: user has been added to the database and a message has been sent
    :status 400: form parameters missing

Confirmation
============

.. http:post:: /v1/customers/user/

    Confirm registration

    :form phone: user phone number
    :form device: device name
    :form pin: pin code received
    :form name: optional name if user's name is not in database

    :>header Content-Type: application/x-www-form-urlencoded

    :<header Content-Type: application/json

    :status 200: token with device exists, new identifier generated
    :status 201: token has been added
    :status 400: form parameters missing

