====
Food
====

List/Create
===========

.. http:get:: /v1/business/food/(datetime:since)/

    List the food of the store or create food with a POST request.

    Permissions: :doc:`/permissions/business/storeOwner`

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


Retrieve/Update
===============

.. http:get:: /v1/business/food/(int:id)/

    Retrieve/patch a food by its ID.

    Permissions: :doc:`/permissions/business/storeOwner`

    Authentication: :doc:`/authentication/employee`

    GET Serializer: :doc:`/serializers/business/storeFood`
    POST Serializer: :doc:`/serializers/business/shortFood`

    :query int id: :doc:`/serializers/global/food` ID


Retrieve Default
================

.. http:get:: /v1/business/food/default/(int:id)/

    Retrieve a food by its ID.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/global/defaultFood`

    :query int id: :doc:`/serializers/global/defaultFood` ID
