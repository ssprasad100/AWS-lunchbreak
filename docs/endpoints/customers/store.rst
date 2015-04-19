=====
Store
=====

Nearby stores
=============

.. http:get:: /v1/customers/store/nearby/(decimal:latitude)/(decimal:longitude)/(number:proximity)/

    Stores within a proximity.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/global/store`

    :query decimal latitude: latitude coordinate
    :query decimal longitude: longitude coordinate
    :query number proximity: proximity, default is 5 km

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed


Specific store
==============

.. http:get:: /v1/customers/store/(int:id)/

    Store with the given ID.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/global/store`

    :query int id: ID of the store

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed


Opening hours and holiday periods
=================================

.. http:get:: /v1/customers/store/open/(int:id)/

    Authentication: :doc:`/authentication/user`

    Show the opening hours of a specific store.

    :query int id: ID of the store

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed

    :resjson objectarray holidayPeriods: :doc:`/serializers/global/holidayPeriod`
    :resjson objectarray openingHours: :doc:`/serializers/global/openingHours`


Opening hours
=============

.. http:get:: /v1/customers/store/hours/(int:id)/

    Show the opening hours of a specific store.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/global/openingHours`

    :query int id: ID of the store

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed



Holiday periods
===============

.. http:get:: /v1/customers/store/holiday/(int:id)/

    Show upcoming holiday periods of the store this week.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/global/holidayPeriod`

    :query int id: ID of the store

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed
