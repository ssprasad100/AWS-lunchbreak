=====
Store
=====

Nearby stores
=============

.. http:get:: /v1/customers/store/nearby/(double:latitude)/(double:longitude)/(number:proximity)

    Stores within a proximity.

    Serializer: :doc:`/serializers/global/store`

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :query double latitude: latitude coordinate
    :query double longitude: longitude coordinate
    :query number proximity: proximity, default is 5 km

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed


Specific store
==============

.. http:get:: /v1/customers/store/(int:store_id)

    Store with the given ID.

    Serializer: :doc:`/serializers/global/store`

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :query int store_id: ID of the store

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed


Opening hours and holiday periods
=================================

.. http:get:: /v1/customers/store/hours/(int:store_id)

    Show the opening hours of a specific store.

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :query int store_id: ID of the store

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed

    :resjson objectarray holidayPeriods: :doc:`/serializers/global/holidayPeriod`
    :resjson objectarray openingHours: :doc:`/serializers/global/openingHours`


Opening hours
=============

.. http:get:: /v1/customers/store/hours/(int:store_id)

    Show the opening hours of a specific store.

    Serializer: :doc:`/serializers/global/openingHours`

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :query int store_id: ID of the store

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed



Holiday periods
===============

.. http:get:: /v1/customers/store/holiday/(int:store_id)

    Show upcoming holiday periods of the store this week.

    Serializer: :doc:`/serializers/global/holidayPeriod`

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :query int store_id: ID of the store

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed
