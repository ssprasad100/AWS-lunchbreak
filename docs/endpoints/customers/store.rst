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


Specific store
==============

.. http:get:: /v1/customers/store/(int:id)/

    Store with the given ID.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/global/store`

    :query int id: ID of the store


Heart/unheart store
===================

.. http:get:: /v1/customers/store/(string:option)/(int:id)/

    Store with the given ID.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/global/store`

    :query string option: Heart/unheart, unheart default
    :query int id: ID of the store


Opening hours and holiday periods
=================================

.. http:get:: /v1/customers/store/open/(int:id)/

    Authentication: :doc:`/authentication/user`

    Show the opening hours of a specific store.

    :query int id: ID of the store

    :resjson objectarray holidayPeriods: :doc:`/serializers/global/holidayPeriod`
    :resjson objectarray openingHours: :doc:`/serializers/global/openingHours`


Opening hours
=============

.. http:get:: /v1/customers/store/hours/(int:id)/

    Show the opening hours of a specific store.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/global/openingHours`

    :query int id: ID of the store


Holiday periods
===============

.. http:get:: /v1/customers/store/holiday/(int:id)/

    Show upcoming holiday periods of the store this week.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/global/holidayPeriod`

    :query int id: ID of the store
