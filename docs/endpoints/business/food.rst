====
Food
====

List
====

.. http:get:: /v1/business/food/

    List the food of the store.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/shortFood`

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed


List Default
============

.. http:get:: /v1/business/food/default/

    **Pagination disabled.**

    List the food of the store.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/shortFood`

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed


Retrieve
========

.. http:get:: /v1/business/food/(int:id)

    Retrieve a food by its ID.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/global/defaultFood`

    :resheader Content-Type: application/json

    :query int id: :doc:`/serializers/global/food` ID

    :statuscode 200: no error
    :statuscode 403: authentication failed


Retrieve Default
================

.. http:get:: /v1/business/food/default/(int:id)

    Retrieve a food by its ID.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/global/defaultFood`

    :resheader Content-Type: application/json

    :query int id: :doc:`/serializers/global/defaultFood` ID

    :statuscode 200: no error
    :statuscode 403: authentication failed
