====
Food
====

Create
======

.. http:get:: /v1/business/food/

    Create food for the authorised store.

    Permissions: :doc:`/permissions/business/storeOwner`

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/shortFood`


List
====

.. http:get:: /v1/business/food/(datetime:since)/

    List the food of the store.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/shortFood`

    :query datetime since: Optional datetime to return the food that have been modified since that datetime.


List Default
============

.. http:get:: /v1/business/food/default/

    **Pagination disabled.**

    List the food of the store.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/shortFood`


Retrieve
========

.. http:get:: /v1/business/food/(int:id)

    Retrieve a food by its ID.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/storeFood`

    :query int id: :doc:`/serializers/global/food` ID


Retrieve Default
================

.. http:get:: /v1/business/food/default/(int:id)

    Retrieve a food by its ID.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/global/defaultFood`

    :query int id: :doc:`/serializers/global/defaultFood` ID
